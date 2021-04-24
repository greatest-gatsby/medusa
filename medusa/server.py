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

def process_server(args):
    parser = parsers.get_server_parsers()
    args = parser.parse_args(args)
    _servers = get_servers_from_config()

    if (args.action == 'create'):
        create_server(args.path, args.type, args.alias)
    elif (args.action == 'remove'):
        print('REMOV???')
    elif (args.action == 'list'):
        list_servers(_servers)
    elif (args.action == 'scan'):
        scan_directory_for_servers(_servers, "")
    else:
        parser.print_help()

# Search the data directory for any unregistered servers
def scan_directory_for_servers(servers, scan_path = ""):
    if (scan_path == ""):
        data_dir = config.get_config_value('server_directory')
    
    print('Scanning for existing servers in', data_dir)

    dataset = os.scandir(data_dir)
    new_count = 0
    if (dataset is None):
        print('Didn\'t find any servers')
    else:
        if servers != None and len(servers) > 0:
        # remove entries for servers that no longer exist
            for saved in reversed(servers):
                if not os.path.isdir(saved.Path):
                    servers.remove(saved)

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
            regSuccess, servers = register_server(servers, dir.path ,dir_type)
            if regSuccess:
                new_count += 1

    print('Found {} servers'.format(new_count))


# Print the list of servers to console
def list_servers(servers):
    x = PrettyTable()
    x.field_names = ['Alias', 'Path', 'Type']
    x.align = 'l'
    for srv in servers:
        x.add_row([srv.Alias, os.path.relpath(srv.Path, config.get_config_value('server_directory')), srv.Type])

    print(x)

def get_servers_from_config():
    """
    Returns a list of all the servers registered in Medusa's config.
    Since this function will always read from disk, `get_servers()`
    is generally a better way to retrieve the servers, as it prefers
    to read from memory when possible.
    """
    if not os.path.isfile(config.get_config_location()):
        return []
    try:
        with open(config.get_config_location(), 'r') as f:
            data_string = f.read()
            data_set = jsonpickle.decode(data_string)
            data_set = data_set['server_registry']
            return data_set
    except json.JSONDecodeError as jde:
        print('Error decoding data file')
        return []
    except KeyError as ae:
        print('Could not find "servers" node')
        return data_set

def get_servers():
    """
    Returns a list of all of the servers registered with Medusa.
    """
    if _servers is None:
        _servers = get_servers_from_config()
    
    return _servers

# Create a new server
def create_server(path, type = None, alias = None):
    pass

# Remove and delete an existing server
def remove_server(identifier):
    pass

def register_server(servers, path: str, srv_type: ServerType, alias: str = None):
    """
    Links Medusa to a Minecraft server that already exists, adding an entry in the
    central save file and creating a `.medusa` file in the server directory.

    Parameters
    ----------
        servers : list of Server
            The servers registered with Medusa.
    
    Returns
    -------
        bool : success
            `True` if the operation succeeded, or `False` if the server was already registered.

    Raises
    ------
        JsonEncodeError, JsonDecodeError
            If there is an error encoding or decoding the config file
        
        IOError
            If there is an error reading or writing the config file from/to disk.
    """
    if servers == None:
        servers = []

    new = Server()
    new.Path = os.path.abspath(path)
    new.Type = srv_type
    new.Alias = alias
    if alias:
        alias = alias.strip()

    if servers is not None and len(servers) > 0:
        for srv in servers:
            if (srv.Path == new.Path):
                return False
            if (srv.Alias == new.Alias and srv.Alias):
                return False

    servers.append(new)

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
                data['server_registry'] = servers
                encoded = jsonpickle.encode(data)
                data_file.write(encoded)
            except json.JSONEncodeError as ex:
                print('Error writing servers file while registering new server', ex)
                raise

        # success
        print('Registered', srv_type, 'server at', path)
        return True

    except json.JSONDecodeError as ex:
        print("Error writing servers to disk", ex)
        raise

# returns a server's type given the path to the server directory
def determine_server_type(srv_dir: str):
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
                else:
                    strat_jar = ServerType.VANILLA
            
            # strat 2 - yml files
            if file.endswith('.yml') or file.endswith('yaml'):
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