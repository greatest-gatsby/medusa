# Medusa imports
from . import config
from . import server
from . import status

def add_config_parsers(main_parser, main_subparser):
    config_parser = main_subparser.add_parser('config')
    config_subparsers = config_parser.add_subparsers(dest='action')
    config_get_parser = config_subparsers.add_parser('get')
    config_set_parser = config_subparsers.add_parser('set')
    config_init_parser = config_subparsers.add_parser('init')
    config_where_parser = config_subparsers.add_parser('where')

    config_get_parser.add_argument('property', help='Property to get/set')
    config_set_parser.add_argument('property', help='Property to get/set')
    config_set_parser.add_argument('value', help='New value')
    config_init_parser.add_argument('-p', '--path', help='Path to directory or file to use as application storage')

def add_server_parsers(main_parser, main_subparser):
    server_parser = main_subparser.add_parser('server')
    server_subparsers = server_parser.add_subparsers(dest='action')

    server_create_parser = server_subparsers.add_parser('create')
    server_create_parser.add_argument("path", help='Path to directory relative to the server directory')
    server_create_parser.add_argument('-a', '--alias')
    server_create_parser.add_argument('-t', '--type', help='Type of server',
        choices=['vanilla', 'forge', 'spigot', 'paper'])

    server_remove_parser = server_subparsers.add_parser('remove')
    server_list_parser = server_subparsers.add_parser('list')
    server_scan_parser = server_subparsers.add_parser('scan')

    server.serv_subparser = server_parser
    
def add_status_parsers(main_parser, main_subparser):
    status_parser = main_subparser.add_parser('status')
    status_parser.add_argument('--server', '-s',
        help='Name of the server')

def add_user_parsers(main_parser, main_subparser):
    user_parser = main_subparser.add_parser('user')
    user_subparsers = user_parser.add_subparsers(help='Manage Users', dest='user', description='Manage users')
    user_list_parser = user_subparsers.add_parser('list')