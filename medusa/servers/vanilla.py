import argparse
from os import PathLike
import os
from typing import Union

from medusa.servers import VANILLA

from .models import ServerController, Server
from .. import parsers

def is_path_vanilla(directory: PathLike) -> bool:
    """
    Determines whether the given path points to a vanilla server
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
                if 'mc' in file or 'minecraft' in file:
                    strat_jar =  True
                    
    return strat_jar

class VanillaServer(Server):
    def __init__(self):
        super().__init()
        self.Type = VANILLA

class VanillaController(ServerController):
    """
    Provides control of a vanilla Minecraft server.
    """

    def __init__(self):
        pass

    def __init__(self, srv: Server):
        if srv.Type != VANILLA:
            raise TypeError('Expected Vanilla server but got {}'.format(srv.Type))
        
        self.info = srv

    def startup(cls):
        print('Starting server')

    def shutdown(cls):
        print('Shutting down server')

    @classmethod
    def get_parser(cls):
        run_parser = super().get_parser(cls)
        return run_parser