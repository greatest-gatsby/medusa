import io
import json
from json import JSONDecodeError
import os

from . import filebases
from . import parsers

APP_NAME = 'medusa'
APP_AUTHOR = 'Jay Rode'
CONFIG_NAME = 'medusa.json'

def process_config(args):
    """
    Consumes command-line arguments and branches into whatever command specified by the user.
    Nothing is returned and no error is thrown.

    Parameters
    ----------
        args : list of str
    """
    parser = parsers.get_config_parsers()
    cmd = parser.parse_args(args)

    if (cmd.action == 'get'):
        val = get_config_value(cmd.property)
        if (val is None):
            print('No key named', cmd.property)
        else:
            print(val)
    elif (cmd.action == 'set'):
        set_config_value(cmd.property, cmd.value)
    elif (cmd.action == 'init'):
        init_config(cmd.path)
    elif (cmd.action == 'where'):
        print(get_config_location())
    else:
        parser.print_usage()
        print('Please specify a subcommand for `config`')

def get_config_value(key: str):
    """
    Returns the value specified by the key, or None if key was not found.
    
    Parameters
    ----------
    key : str
        The key whose value will be retrieved. If the string is null
        or empty, then a KeyError will be raised.

    
    Raises
    ------
        KeyError
            If the given key is null or empty.
    """
    if key is None or key == "":
        raise KeyError
    try:
        with open(get_config_location(), 'r') as dat:
            obj = json.load(dat)
            return obj[key]            
    except FileNotFoundError:
        raise
    except:
        return

def set_config_value(key, value):
    """
    Sets the value of a given key in the Medusa config.

    Parameters
    ----------
        key : str
            The key whose value will be set. If the string is null
            or empty, then a KeyError will be raised.
        value : Any
            The value to set. 
    
    Raises
    ------
        KeyError
            If the given key is null or empty
    """
    try:
        file = open(get_config_location(), 'r')
        obj = json.load(file)
    except JSONDecodeError as jer:
        if jer.lineno == 1 and jer.colno == 1:
            print('Config file empty -- generate a new one with `medusa config init`')
            exit(1)
        else:
            print(jer)
        print('Error opening config for write -- file is malformed or corrupt')
        raise
    except FileNotFoundError as fnf:
        print('Config not found at', get_config_location())
        raise
    except:
        print("Unknown error opening config for write")
        raise

    obj[key] = value
    try:
        with open(get_config_location(), 'w') as file:
            json.dump(obj, file)
    except:
        print('Error writing updated config to disk')
        raise
    

def init_config(verbosity = None):
    """
    Writes a plain config to disk, prompting if the operation
    would overwrite existing data.
    """
    if (os.path.exists(get_config_location())):
        print('Initializing a new config will overwrite the one at',get_config_location())
        res = input('Are you SURE you want to OVERWRITE this file? [y/N]: ')
        if res.strip().lower() != 'y':
            if (verbosity is not None):
                print('Config init aborted.')
            return False
    # create directory if not exists
    if not (os.path.isdir(os.path.dirname(get_config_location()))):
        os.makedirs(os.path.dirname(get_config_location()))
    
    # open and write
    with open(get_config_location(), 'w') as file:
        file.write(filebases.DATA)
    
    # print result
    print('Created new Medusa config at', os.path.abspath(get_config_location()))

def get_config_location():
    return "data/medusa.json"