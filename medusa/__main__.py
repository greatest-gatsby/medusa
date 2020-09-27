import argparse
import os
import subprocess
import sys
import inspect

# Medusa imports
from . import config
from . import server
from . import status

# top-level parser
parser = argparse.ArgumentParser(description='Manage multiple Spigot Minecraft servers')
subparsers = parser.add_subparsers(help='Available commands', dest='command',
    title='command', description='Main command to execute')

# 'config' command
config_parser = subparsers.add_parser('config')
config_subparsers = config_parser.add_subparsers(dest='action')
config_get_parser = config_subparsers.add_parser('get')
config_set_parser = config_subparsers.add_parser('set')
config_init_parser = config_subparsers.add_parser('init')
config_where_parser = config_subparsers.add_parser('where')

config_get_parser.add_argument('property', help='Property to get/set')
config_set_parser.add_argument('property', help='Property to get/set')
config_set_parser.add_argument('value', help='New value')
config_init_parser.add_argument('-p', '--path', help='Path to directory or file to use as application storage')

# 'server' command
server_parser = subparsers.add_parser('server')
server_subparsers = server_parser.add_subparsers(dest='action')

server_create_parser = server_subparsers.add_parser('create')
server_create_parser.add_argument("path", help='Path to directory relative to the server directory')
server_create_parser.add_argument('-a', '--alias')
server_create_parser.add_argument('-t', '--type', help='Type of server',
    choices=['vanilla', 'forge', 'spigot', 'paper'])

server_remove_parser = server_subparsers.add_parser('remove')
server_list_parser = server_subparsers.add_parser('list')
server_scan_parser = server_subparsers.add_parser('scan')

# 'status' command
status_parser = subparsers.add_parser('status')
status_parser.add_argument('--server', '-s',
    help='Name of the server')

# 'user' command
user_parser = subparsers.add_parser('user')
user_subparsers = user_parser.add_subparsers(help='Manage Users', dest='user', description='Manage users')
user_list_parser = user_subparsers.add_parser('list')


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