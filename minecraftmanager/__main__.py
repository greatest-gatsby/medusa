import argparse
import os
import subprocess
import sys
import inspect

# Medusa imports
import config
import status

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

# 'status' command
status_parser = subparsers.add_parser('status')
status_parser.add_argument('--server', '-s',
    help='Name of the server')

# 'user' command
user_parser = subparsers.add_parser('user')
user_subparsers = user_parser.add_subparsers(help='Manage Users', dest='user', description='Manage users')
user_list_parser = user_subparsers.add_parser('list')


if __name__ == '__main__':
    args = parser.parse_args()
    if (args.command == 'config'):
        config.process_config(args)
    elif (args.command == 'status'):
        status.process_status(args)