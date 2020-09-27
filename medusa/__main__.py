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
server.servers = server.get_servers_from_data_file()

if __name__ == '__main__':
    args = parser.parse_args()
    if (args.command == 'config'):
        config.process_config(args)
    elif (args.command == 'status'):
        status.process_status(args)
    elif (args.command == 'server'):
        server.process_server(args)