import argparse

from .models import ServerController, ServerType, Server

from ..parsers import parser
from ..parsers import subparsers

class ForgeController(ServerController):
    """
    Provides control of a Forge-based Minecraft server.
    """

    def __init__(self):
        pass

    def __init__(self, srv: Server):
        if srv.Type != ServerType.FORGE:
            raise TypeError('Expected Forge server but got {}'.format(srv.Type))
        
        self.info = srv

    def startup(cls):
        print('Starting Forge server')
        pass

    def shutdown(cls):
        pass

    @classmethod
    def get_parser(cls):
        run_parser = subparsers.add_parser('run')
        run_parser.add_argument('identifier', help='Alias or path of the server')
        run_parser.add_argument('command', nargs='+')
        return parser