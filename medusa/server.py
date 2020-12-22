from enum import Enum
import io
import json
import os
from pprint import pprint
import argparse

import jsonpickle

from . import config

servers = []
serv_subparser = None

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
    if (args.action == 'create'):
        create_server(args.path, args.type, args.alias)
    elif (args.action == 'remove'):
        print('REMOV???')
    elif (args.action == 'list'):
        list_servers()
    elif (args.action == 'scan'):
        scan_servers()
    else:
        serv_subparser.print_help()

# Search the data directory for any unregistered servers
def scan_servers():
    data_dir = config.get_config_value('server_directory')
    print('Scanning for existing servers in', data_dir)

    dataset = os.scandir(data_dir)
    new_count = 0
    if (dataset is None):
        print('Didn\'t find any servers')
    else:
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
            if (register_server(dir.path ,dir_type)):
                new_count += 1

    print('Found {} servers'.format(new_count))
    pass


# Print the list of servers to console
def list_servers():
    for srv in servers:
        print(srv)
    pass

    #for root, dirs, files in os.walk(data_dir):
    #    print('Root:', root)
    #    print('Dirs:', dirs)
    #    print('Files:', files)

# Get a list of the Servers stored in the config file
def get_servers_from_data_file():
    try:
        with open(config.get_data_location(), 'r') as f:
            data_string = f.read()
            data_set = jsonpickle.decode(data_string)['servers']
            return data_set
    except json.JSONDecodeError as jde:
        print('Error decoding data file')
        return
    except AttributeError as ae:
        print('Could not find "servers" node')
        return

# Create a new server
def create_server(path, type = None, alias = None):
    pass

# Register an existing server with the application
def register_server(path: str, srv_type: ServerType, alias: str = None):
    new = Server()
    new.Path = os.path.abspath(path)
    new.Type = srv_type
    new.Alias = alias

    for srv in servers:
        if (srv.Path == new.Path):
            print("Server with path '{}' already registered".format(srv.Path))
            return False
        if (srv.Alias and srv.Alias == new.Alias):
            print("Server with alias '{}' already registered".format(srv.Alias))
            return False
    
    servers.append(new)

    try:
        with open(config.get_data_location(), 'r') as data_file:
            try:
                data = jsonpickle.decode(data_file.read())
            except json.JSONDecodeError as ex:
                print('Error reading servers file while registering new server', ex)
                return False
        
        with open(config.get_data_location(), 'w') as data_file:
            try:
                data['servers'] = servers
                encoded = jsonpickle.encode(data)
                data_file.write(encoded)

                # success
                print('Registered', srv_type, 'server at', path)
                return True
            except json.JSONEncodeError as ex:
                print('Error writing servers file while registering new server', ex)
                return False

    except json.JSONDecodeError as ex:
        print("Error writing servers to disk", ex)
        return False

# determine a server's type given the path to the server directory
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