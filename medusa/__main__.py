import argparse
import os
import subprocess
import sys
import inspect

# Medusa imports
from . import config
from . import parsers
from . import server
from . import status

# top-level parser
parser = argparse.ArgumentParser(description='Manage multiple Spigot Minecraft servers')
subparsers = parser.add_subparsers(help='Available commands', dest='command',
    title='command', description='Main command to execute')

# 'config' command
parsers.add_config_parsers(parser, subparsers)

# 'server' command
parsers.add_server_parsers(parser, subparsers)

# 'status' command
parsers.add_status_parsers(parser, subparsers)

# 'user' command
parsers.add_user_parsers(parser, subparsers)

# init submodules
servers = server.get_servers_from_config()


if __name__ == '__main__':
    # args = parser.parse_args()
    # screw argparse
    # we split off each of the first words, then parse the command once we hit a full command word

    if len(sys.argv) < 2:
        cmd = ""
    else:
        cmd = sys.argv[1]
    
    
    if (cmd == 'config'):
        config.process_config(sys.argv[2:])
    elif (cmd == 'status'):
        status.process_status(args)
    elif (cmd == 'server'):
        server.process_server(args, servers)
    else:
        print("HELP HERE")