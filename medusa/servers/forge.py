import argparse
from os import PathLike
import os
from typing import Union

from .models import ServerController, ServerType, Server
from .. import parsers

def is_path_forge(directory: PathLike) -> bool:
    """
    Determines whether the given path points to a forge server
    """
    srv_dir = os.path.abspath(directory)
    strat_jar = False
    for dir_path, dir_names, f_names in os.walk(srv_dir):
        # don't enter subdirectories
        if dir_path != srv_dir:
            continue        

        # iterate through file names, recording each strategy's guess
        for file in f_names:
            file = file.lower()

            # strat 1 - jar files
            if file.endswith('.jar'):
                if 'forge' in file:
                    strat_jar =  True
                    
    return strat_jar

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

    def shutdown(cls):
        print('Shutting down Forge server')

    @classmethod
    def get_parser(cls):
        run_parser = super().get_parser(cls)
        return run_parser