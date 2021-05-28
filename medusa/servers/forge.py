import argparse

from .models import ServerController, ServerType, Server
from .. import parsers



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
        run_parser = super().get_parser(cls)
        return run_parser