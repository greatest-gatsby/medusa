from enum import Enum
import io
import json
import os
from pprint import pprint
from prettytable import PrettyTable
import argparse

import jsonpickle

from . import config
from . import filebases
from . import parsers

serv_subparser = None
_servers = []

class ServerType(Enum):
    NOTASERVER = 0
    VANILLA = 1
    FORGE = 2
    SPIGOT = 4
    PAPER = 8

class Server:
    Path: str
    Alias: str
    Type: ServerType

    def __str__(self):
        return "{}\t{}\t{}".format(self.Alias, self.Path, self.Type)

    def __eq__(self, other):
        return self.is_identifiable_by(other)

    def is_identifiable_by(this, identifier: str):
        """
        Determines whether the given string is a valid identifier for this server.
        Works by matching Alias then Path, in that order.

        Returns
        ------
            boolean
                `True` if the given string identifies this server, else `False`.
        """
        if this.Alias == identifier or this.Path == identifier:
            return True
        
        return False

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
    else:
        parser.print_help()

def scan_directory_for_servers(scan_path: str = ""):
    """
    Searches the named directory for any servers that aren't
    already registered. Returns the new servers that were discovered.

    Parameters
    ----------
        scan_path: str
            Path to the directory to scan. If omitted, the server directory
            set in the config will be used. File-access exceptions are not caught
            within this method!

    Returns
    -------
        count: Number of added Servers
            The number of new Servers that were registered with Medusa.
            Returns zero if no new servers were registered during the scan.
    """
    if (scan_path == ""):
        data_dir = config.get_config_value('server_directory')
    
    print('Scanning for existing servers in', data_dir)

    dataset = os.scandir(data_dir)
    new_count = 0
    if (dataset is None):
        print('Didn\'t find any servers')
        return 0
    else:
        if _servers != None and len(_servers) > 0:
        # remove entries for servers that no longer exist
            for saved in reversed(_servers):
                if not os.path.isdir(saved.Path):
                    _servers.remove(saved)

        # scan for servers in the server directory
        for dir in dataset:
            # reject non-dirs
            if not dir.is_dir:
                continue
            
            # reject non-servers unless user manually adds them
            dir_type = determine_server_type(dir.path)
            if dir_type == ServerType.NOTASERVER:
                continue
            
            # record any successes
            regSuccess, _servers = register_server(dir.path ,dir_type)
            if regSuccess:
                new_count += 1

        print('Found {} servers'.format(new_count))
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

def get_servers_from_config():
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
    try:
        with open(config.get_config_location(), 'r') as f:
            data_string = f.read()
            data_set = jsonpickle.decode(data_string)
            data_set = data_set['server_registry']
            return data_set
    except json.JSONDecodeError as jde:
        print('Error decoding data file')
        raise
    except KeyError as ae:
        print('Could not find "servers" node')
        raise

def get_servers():
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
    global _servers
    if _servers == None:
        _servers = []

    new = Server()
    new.Path = os.path.abspath(path)
    new.Type = srv_type
    new.Alias = alias
    if alias:
        alias = alias.strip()

    if _servers is not None and len(_servers) > 0:
        for srv in _servers:
            if (srv.Path == new.Path):
                return False
            if (srv.Alias == new.Alias and srv.Alias):
                return False

    _servers.append(new)

    try:
        # Read in current config
        with open(config.get_config_location(), 'r') as data_file:
            try:
                data = jsonpickle.decode(data_file.read())
            except json.JSONDecodeError as ex:
                print('Error reading servers file while registering new server')
                raise
        
        # Write .medusa to the server directory
        with open(os.path.join(new.Path,'.medusa'), 'w') as dotmedusa:
            try:
                # If alias is given, then the base dotmedusa file must be modified before writing to disk
                if new.Alias:
                    dm = json.loads(filebases.DOT_MEDUSA)
                    dm["metadata"]["alias"] = new.Alias
                    dotmedusa.write(json.dumps(dm))
                else:
                    dotmedusa.write(filebases.DOT_MEDUSA)
            except:
                print('Error writing .medusa to', os.path.join(new.Path,'.medusa') ,'. Does this user have permission to write there?')
                raise

        # Write entry to server_reigstry in config
        with open(config.get_config_location(), 'w') as data_file:
            try:
                data['server_registry'] = _servers
                encoded = jsonpickle.encode(data)
                data_file.write(encoded)
            except json.JSONEncodeError as ex:
                print('Error writing servers file while registering new server', ex)
                raise

        # success
        # print('Registered', srv_type, 'server at', path)
        return True

    except json.JSONDecodeError:
        print("Error writing servers to disk")
        raise

def determine_server_type(srv_dir: str):
    """
    Examines the files in a given server directory to determine its type.
    Currently the search works primarily on key file names. For example,
    Spigot and Forge both include their names in the jar filenames.

    Parameters
    ----------
        srv_dir: str
            Path to server directory to be examined.

    Returns
    -------
        ServerType
            Type of Minecraft server this was determined to be
    """
    srv_dir = os.path.abspath(srv_dir)
    for dir_path, dir_names, f_names in os.walk(srv_dir):
        # don't enter subdirectories
        if dir_path != srv_dir:
            continue
        
        # strategies:
        #   1   .jar files
        #   2.  .yml config files
        strat_jar = ServerType.NOTASERVER
        strat_yml = ServerType.NOTASERVER

        # iterate through file names, recording each strategy's guess
        for file in f_names:
            file = file.lower()

            # strat 1 - jar files
            if file.endswith('.jar'):
                if 'spigot' in file:
                    strat_jar =  ServerType.SPIGOT
                elif 'forge' in file:
                    strat_jar =  ServerType.FORGE
                elif 'paper' in file:
                    strat_jar = ServerType.PAPER
                #else:
                #    strat_jar = ServerType.VANILLA
            
            # strat 2 - yml files
            if file.endswith('.yml') or file.endswith('.yaml'):
                if 'spigot' in file:
                    strat_yml =  ServerType.SPIGOT
                elif 'forge' in file:
                    strat_yml =  ServerType.FORGE
                elif 'paper' in file:
                    strat_yml = ServerType.PAPER

        # assume notasever
        # return consensus if it is a server
        if strat_jar == strat_yml and strat_jar != ServerType.NOTASERVER:
            return strat_jar
        else:
            # skip strat 1 if it said not a server
            if strat_jar == ServerType.NOTASERVER:
                return strat_yml
            else:
                return strat_jar