import argparse

# top-level parser
parser = argparse.ArgumentParser(description='Manage multiple Spigot Minecraft servers')
subparsers = parser.add_subparsers(help='Available commands', dest='command',
    title='command', description='Main command to execute')

arg_verbose = argparse.ArgumentParser(add_help=False)
arg_verbose.add_argument('--verbose', '-v', action='count', default=0)

arg_identifier = argparse.ArgumentParser(add_help=False)
arg_identifier.add_argument('identifier', help='Alias or path of the server to remove')



def get_config_parsers():
    config_parser = subparsers.add_parser('config')
    config_subparsers = config_parser.add_subparsers(dest='action')
    config_get_parser = config_subparsers.add_parser('get', parents=[arg_verbose])
    config_set_parser = config_subparsers.add_parser('set', parents=[arg_verbose])
    config_init_parser = config_subparsers.add_parser('init', parents=[arg_verbose])
    config_where_parser = config_subparsers.add_parser('where', parents=[arg_verbose])

    config_get_parser.add_argument('property', help='Property to get/set')
    config_set_parser.add_argument('property', help='Property to get/set')
    config_set_parser.add_argument('value', help='New value')
    config_init_parser.add_argument('-p', '--path', help='Path to directory or file to use as application storage')

    return config_parser

def get_server_parsers():
    server_parser = subparsers.add_parser('server')
    server_subparsers = server_parser.add_subparsers(dest='action')

    server_create_parser = server_subparsers.add_parser('create', parents=[arg_verbose])
    server_create_parser.add_argument("path", help='Path to directory relative to the server directory')
    server_create_parser.add_argument('-a', '--alias')
    server_create_parser.add_argument('-t', '--type', help='Type of server',
        choices=['vanilla', 'forge', 'spigot', 'paper'])

    server_remove_parser = server_subparsers.add_parser('remove', parents=[arg_identifier, arg_verbose])
    server_list_parser = server_subparsers.add_parser('list')
    server_scan_parser = server_subparsers.add_parser('scan')
    server_scan_parser.add_argument('-p', '--path', help='Path to directory to be scanned')

    return server_parser
    
def add_status_parsers(main_parser, main_subparser):
    status_parser = main_subparser.add_parser('status')
    status_parser.add_argument('--server', '-s',
        help='Name of the server')

def add_user_parsers(main_parser, main_subparser):
    user_parser = main_subparser.add_parser('user')
    user_subparsers = user_parser.add_subparsers(help='Manage Users', dest='user', description='Manage users')
    user_list_parser = user_subparsers.add_parser('list')