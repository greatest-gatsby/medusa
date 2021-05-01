import abc
from enum import Enum
import os
import pathlib

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
        pass

    @abc.abstractmethod
    def startup(cls):
        print('Starting abstract')
        pass

    @abc.abstractmethod
    def shutdown(cls):
        pass

    def find_startup_script_paths(self):
        """
        Finds the startup scripts, if any, for this Server.

        Returns
        -------
            paths: List of str
                The path to the scripts, or an empty list
                if no such script was found. The paths are
                relative to the root of the server directory.
        """
        path = pathlib.Path(self.info.Path)
        found = []
        target_ext = ['.bat', '.sh']

        with os.scandir(path) as scan:
            for file in scan:
                if not file.is_file():
                    continue
                for ext in target_ext:
                    if file.name.endswith(ext) and 'start' in file.name:
                        found.append(file.name)
        
        return found