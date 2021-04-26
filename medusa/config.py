import io
import json
import os

import appdirs

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
        if len(args) < 2:
            print('No key specified')
            return
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
        if not (os.path.getsize(get_config_location())):
            print('Config is empty -- generate a new one with `medusa config init`')
            exit(code=1)
        file = open(get_config_location(), 'r')
        obj = json.load(file)
    except json.JSONDecodeError as jer:
        print('Error opening config for write -- file is malformed or corrupt')
        raise
    except FileNotFoundError as fnf:
        print('Config not found at', get_config_location())
        raise
    except:
        print("Unknown error opening config for write")
        raise

    if (key in obj):
        obj[key] = value
        try:
            with open(get_config_location(), 'w') as file:
                json.dump(obj, file)
        except:
            print('Error writing updated config to disk')
    else:
        print('No key named', key)
    

def init_config(path):
    # use given path and default name if given path is a directory
    if (os.path.exists(get_config_location())):
        print('Initializing a new config will overwrite the one at',get_config_location())
        res = input('Are you SURE you want to OVERWRITE this file? [y/N]: ')
        if res != 'y' and res != 'Y':
            print("Init aborted")
            exit(1)
    # create directory if not exists
    if not (os.path.isdir(os.path.dirname(get_config_location()))):
        try:
            os.makedirs(os.path.dirname(get_config_location()))
        except:
            print('Error occured while creating config directory')
            return
    
    # open and write
    try:
        with open(get_config_location(), 'w') as file:
            file.write(filebases.DATA)
    except:
        print('Error occured while writing new config')
        return
    
    # print result
    print('Created new Medusa config at', os.path.abspath(get_config_location()))

def get_config_location():
    return "data/medusa.json"
    return os.path.join(
        appdirs.site_config_dir(APP_NAME, APP_AUTHOR),
        'medusa.json'
    )

def get_data_location():
    return "data/medusa-data.json"
    return os.path.join(
        appdirs.site_config_dir(APP_NAME, APP_AUTHOR),
        'medusa-data.json'
    )