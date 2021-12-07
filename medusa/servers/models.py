import abc
from enum import Enum
import os
from pathlib import PurePath
from typing import Union

from .. import parsers

class Server:
    """
    Represents a Minecraft server and its general information.
    Any type-specific info (e.g. Forgeloader version) requires a
    corresponding Controller.
    """
    
    Path: str = ''
    """Path to the server"""
    
    Alias: str = ''
    """Human-friendly name for the server"""

    Type: str
    """Type of the server"""

    def __str__(self):
        return "{}\t{}\t{}".format(self.Alias, self.Path, self.Type)

    def __eq__(self, other):
        return self.is_identifiable_by(other)

    def is_identifiable_by(self, identifier: str):
        """
        Determines whether the given string is a valid identifier for this server.
        Works by matching Alias then Path, in that order.

        Returns
        ------
            boolean
                `True` if the given string identifies this server, else `False`.
        """
        if self.Alias == identifier or self.Path == identifier:
            return True
        
        # match directory name of a server
        parts = PurePath(self.Path).parts
        if identifier == parts[-1]:
            return True
        
        return False

class ServerController(abc.ABC):
    info: Server
    """Information regarding this server"""
    
    startup_script_path: str
    """Path to the startup script"""
    
    @abc.abstractmethod
    def get_parser(cls):
        run_parser = parsers.get_run_parsers()
        run_subs = run_parser.add_subparsers(dest='action')

        passthru_parser = run_subs.add_parser('pass', help='Passes the given command to the Minecraft server directly')
        passthru_parser.add_argument('command', help='Command to execute in server console')
        start_parser = run_subs.add_parser('start')
        stop_parser = run_subs.add_parser('stop')
        restart_parser = run_subs.add_parser('restart')
        
        return run_parser

    @abc.abstractmethod
    def startup(cls):
        print('Starting abstract')
        pass

    @abc.abstractmethod
    def shutdown(cls):
        pass


__supported_server_types = []

def add_supported_server_type(name: str, info: Server, controller: ServerController):
    global __supported_server_types
    if (is_type_supported(name)):
        print('Already know type',name)
    
    __supported_server_types.append({'name':name, 'info': info, 'controller': controller})
    
def get_supported_type(name: str) -> Union[dict, None]:
    global __supported_server_types
    for supported in __supported_server_types:
        if supported['name'] == name:
            return supported
        
    return None

def is_type_supported(type: Union[str, Server, ServerController]) -> bool:
    if isinstance(type, str):
        for supported in __supported_server_types:
            if supported['name'] == type:
                return True
            
    elif isinstance(type, Server):
        for supported in __supported_server_types:
            if supported['info'] == type:
                return True
            
    elif isinstance(type, ServerController):
        for supported in __supported_server_types:
            if supported['controller'] == type:
                return True
            
    return False