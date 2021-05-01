import abc
from enum import Enum
import os
import pathlib

from .. import parsers

class ServerType(Enum):
    NOTASERVER = 0
    VANILLA = 1
    FORGE = 2
    SPIGOT = 4
    PAPER = 8

class Server:
    Path: str
    Alias: str
    Type: ServerType

    def __str__(self):
        return "{}\t{}\t{}".format(self.Alias, self.Path, self.Type)

    def __eq__(self, other):
        return self.is_identifiable_by(other)

    def is_identifiable_by(this, identifier: str):
        """
        Determines whether the given string is a valid identifier for this server.
        Works by matching Alias then Path, in that order.

        Returns
        ------
            boolean
                `True` if the given string identifies this server, else `False`.
        """
        if this.Alias == identifier or this.Path == identifier:
            return True
        
        return False
        

class ServerController(abc.ABC):
    info: Server
    
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
