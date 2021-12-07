from enum import Enum
import io
import json
import os
import pathlib
from pprint import pprint
from types import new_class
from prettytable import PrettyTable
import argparse

import jsonpickle

from medusa.servers import fabric, vanilla

from .. import config
from .. import filebases
from .. import parsers
from .models import Server
from .models import ServerType
from . import forge

serv_subparser = None
_servers = None

def process_server(args):
    """
    Process CLI arguments for `server` commands. This method should really
    only be called from the main parsing logic; it provides verbose, human-friendly
    access to methods that can be more easily invoked programatically.

    Parameters
    ----------
        args : List of str
            Command-line arguments from and including the `server` command.
    """
    global _servers
    parser = parsers.get_server_parsers()
    args = parser.parse_args(args)
    _servers = get_servers_from_config()

    if (args.action == 'create'):
        create_server(args.path, args.type, args.alias)
    elif (args.action == 'remove'):
        deregister_server(args.identifier)
    elif (args.action == 'list'):
        list_servers()
    elif (args.action == 'scan'):
        scan_directory_for_servers("")
    elif (args.action == 'set'):
        srv = get_server_by_identifier(args.identifier)
        if (srv is None):
            print('No server "{}"'.format(args.identifier))
            return
        
        if (args.property == 'alias'):
            srv.Alias = args.value
        elif (args.property == 'path'):
            srv.Path = args.value
        elif (args.property == 'type'):
            srv.Type = args.value
        
        update_server(args.identifier, srv)
    else:
        parser.print_help()

def scan_directory_for_servers(scan_path: str = "", verbosity: int = 1):
    """
    Searches the named directory for any servers that aren't
    already registered. Returns the new servers that were discovered.

    Parameters
    ----------
        scan_path: str
            Path to the directory to scan. If omitted, the server directory
            set in the config will be used. File-access exceptions are not caught
            within this method!
            
        verbosity: int
            Level of verbosity to use. The higher the number, the more verbose the output.

    Returns
    -------
        count: Number of added Servers
            The number of new Servers that were registered with Medusa.
            Returns zero if no new servers were registered during the scan.
    """
    global _servers
    if (scan_path == ""):
        data_dir = config.get_config_value('server_directory')
    else:
        data_dir = scan_path
        
    if verbosity > 0:
        print('Scanning for existing servers in', data_dir)

    dataset = os.scandir(data_dir)

    if _servers != None and len(_servers) > 0:
    # remove entries for servers that no longer exist
        for saved in reversed(_servers):
            if not os.path.isdir(saved.Path):
                _servers.remove(saved)

    # scan for servers in the server directory
    new_count = 0
    for dir in dataset:        
        # reject non-servers unless user manually adds them
        dir_type = ServerType.NOTASERVER
        if (forge.is_path_forge(dir.path)):
            dir_type = ServerType.FORGE
        elif (fabric.is_path_fabirc(dir.path)):
            dir_type = ServerType.FABRIC
        elif (vanilla.is_path_vanilla(dir.path)):
            dir_type = ServerType.VANILLA
            
        if dir_type == ServerType.NOTASERVER:
            continue
        
        # record any successes
        regSuccess = register_server(dir.path ,dir_type)
        if regSuccess:
            new_count += 1

    if verbosity > 0:
        if new_count > 0:
            print('Found {} servers'.format(new_count))
        else:
            print('Didn\'t find any servers')
    return new_count



def list_servers():
    """
    Prints a table of the servers to the console. The paths are
    constructed relative to the server directory.
    """
    if len(get_servers()) == 0:
        print('No registered servers')
        return

    x = PrettyTable()
    x.field_names = ['Alias', 'Path', 'Type']
    x.align = 'l'
    srv_dir = config.get_config_value('server_directory')
    for srv in get_servers():
        x.add_row([srv.Alias, os.path.relpath(srv.Path, srv_dir), srv.Type])

    print(x)

def get_servers_from_config() -> list[Server]:
    """
    Returns a list of all the servers registered in Medusa's config.
    Since this function will always read from disk, `get_servers()`
    is generally a better way to retrieve the servers, as it prefers
    to read from memory when possible.

    Raises
    ------
        FileNotFoundError
            If the config file at the path given by `get_config_location()` does not exist.

    Returns
    -------
        List of Servers
            All the Servers registered in the config file.
    """
    if not os.path.isfile(config.get_config_location()):
        raise FileNotFoundError(config.get_config_location(), 'is not a file.')
    with open(config.get_config_location(), 'r') as f:
        data_string = f.read()
        data_set = jsonpickle.decode(data_string)
        data_set = data_set['server_registry']
        return data_set

def get_servers() -> list[Server]:
    """
    Returns a list of all of the servers registered with Medusa.
    """
    global _servers
    if _servers is None:
        _servers = get_servers_from_config()

    return _servers

def get_server_by_identifier(identifier: str):
    """
    Finds the server that can be identified by the given string. If no such server
    is found, then `None` is returned.
    """
    for srv in get_servers():
        if srv.is_identifiable_by(identifier):
            return srv
    
    return None

# Create a new server
def create_server(path, type = None, alias = None):
    pass

def deregister_server(identifier: str):
    """
    Removes an existing server from Medusa's saved data and stops tracking it.

    Parameters
    ----------
        identifier: str
            Path or alias of server to be deregistered.
    
    Raises
    ------
        KeyError
            If no known server matches the given identifier.
        ValueError
            If the given identifier is None or empty.
    """
    # validate arguments
    if identifier is None or identifier.strip() == "":
        raise ValueError('Identifier None or empty')
    
    # get identified server or raise error
    target = None
    for srv in get_servers():
        if srv.is_identifiable_by(identifier):
            target = srv
            _servers.remove(srv)
            break
    if target is None:
        raise KeyError('No server identifiable by', identifier)

    # remove from config
    with open(config.get_config_location(), 'r+') as conf:
        conf_json = jsonpickle.decode(conf.read())
        conf_json['server_registry'].remove(target)
        conf.seek(0)
        conf.write(jsonpickle.encode(conf_json))
        conf.truncate()

def update_server(old_id: str, updated: Server):
    """
    Update a server registered with Medusa given its last-known identifier
    and updated Server object to insert.

    Parameters
    ---------
        old_id: str
            Identifier for the Server to be updated. This doesn't need to identify
            the new `updated` object, just the current entry that needs to be updated.
        
        updated: Server
            Updated Server object to store in Medusa.
    """
    target = get_server_by_identifier(old_id)
    if target is None:
        raise KeyError(f'No server "{old_id}"')

    # Update servers in memory
    _servers.remove(target)
    _servers.append(updated)

    # Read in current config file, write updated server
    path = config.get_config_location()
    with open(path, 'a+') as data_file:
        data_file.seek(0)
        data = jsonpickle.decode(data_file.read())
        data['server_registry'] = _servers
        data_file.write(jsonpickle.encode(data))

    pass

def register_server(path: str, srv_type: ServerType, alias: str = None):
    """
    Links Medusa to a Minecraft server that already exists, adding an entry in the
    central save file and creating a `.medusa` file in the server directory.

    Parameters
    ----------
        srv_type: ServerType
            The type of the server being registered, such as Vanilla or Fabric.

        alias: str (Optional)
            Human-friendly nickname to identify the server
    
    Returns
    -------
        bool : success
            `True` if the operation succeeded, or `False` if the server was already registered.

    Raises
    ------
        JsonEncodeError, JsonDecodeError
            If there is an error encoding or decoding the config file
        
        IOError
            If there is an error reading or writing the config file from/to disk
    """

    new = Server()
    new.Path = os.path.abspath(path)
    new.Type = srv_type
    new.Alias = alias
    if alias:
        alias = alias.strip()

    for srv in get_servers():
        if srv.is_identifiable_by(path):
            return False

    # Read in current config
    with open(config.get_config_location(), 'r') as data_file:
        data = jsonpickle.decode(data_file.read())
    
    # Write .medusa to the server directory
    with open(os.path.join(new.Path,'.medusa'), 'w') as dotmedusa:
        # If alias is given, then the base dotmedusa file must be modified before writing to disk
        if new.Alias:
            dm = json.loads(filebases.DOT_MEDUSA)
            dm["metadata"]["alias"] = new.Alias
            dotmedusa.write(json.dumps(dm))
        else:
            dotmedusa.write(filebases.DOT_MEDUSA)

    # Write entry to server_reigstry in config
    with open(config.get_config_location(), 'w') as data_file:
        set = get_servers()
        set.append(new)
        data['server_registry'] = set
        encoded = jsonpickle.encode(data)
        data_file.write(encoded)
        
    return True

def find_startup_script_paths(path: str):
    """
    Finds the startup scripts, if any, for this Server.

    Returns
    -------
        paths: List of str
            The path to the scripts, or an empty list
            if no such script was found. The paths are
            relative to the root of the server directory.

    Parameters
    ----------
        path: str
            Path to the directory which may contain top-level
            startup scripts.
    """
    path = pathlib.Path(path)
    found = []
    target_ext = ['.bat', '.sh']

    with os.scandir(path) as scan:
        for file in scan:
            if not file.is_file():
                continue
            for ext in target_ext:
                if file.name.endswith(ext) and 'start' in file.name:
                    found.append(file.name)
    
    return found