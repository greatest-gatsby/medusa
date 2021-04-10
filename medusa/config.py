import io
import json
import os

import appdirs

from . import filebases

APP_NAME = 'medusa'
APP_AUTHOR = 'Jay Rode'
CONFIG_NAME = 'medusa.json'

def process_config(args):
    if len(args) == 0:
        print('Please specify a subcommand for "config"')
        return

    if (args[0] == 'get'):
        if len(args) < 2:
            print('No key specified')
            return
        val = get_config_value(args[1])
        if (val is None):
            print('No key named', args[1])
        else:
            print(val)
    elif (args[0] == 'set'):
        set_config_value(args.property, args.value)
    elif (args[0] == 'init'):
        init_config(args.path)
    elif (args[0] == 'where'):
        print(get_config_location())
    else:
        print('Unknown command', args[0])

# Returns the value specified by the key, or None if key was not found
def get_config_value(key):
    if key is None or key == "":
        print('No key specified')
        return
    try:
        with open(get_config_location(), 'r') as dat:
            obj = json.load(dat)
            return obj[key]            
    except FileNotFoundError:
        print('Config not found at', get_config_location())
        raise
    except:
        print('No key', key)

def set_config_value(key, value):
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