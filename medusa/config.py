import io
import json
import os

import appdirs

APP_NAME = 'medusa'
APP_AUTHOR = 'Jay Rode'
CONFIG_NAME = 'medusa.json'

def process_config(args):
    if (args.action == 'get'):
        val = get_config_value(args.property)
        if (val is None):
            print("No key named", args.property)
        else:
            print(val)
    elif (args.action == 'set'):
        set_config_value(args.property, args.value)
    elif (args.action == 'init'):
        init_config(args.path)
    elif (args.action == 'where'):
        print(get_config_location())
    else:
        print('Please specify a subcommand for "config"')

def get_config_value(key):
    try:
        dat = open(get_config_location(), 'r')
        obj = json.load(dat)
        return obj[key]            
    except:
        print("Failure")

def set_config_value(key, value):
    try:
        obj = json.load(open(get_config_location(), 'r'))
    except:
        print('Error opening config for write')

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
    if (path is str and os.path.isdir(path)):
        file_path = os.path.join(path,CONFIG_NAME)
    elif (path is None or path == ''):
        file_path = ''

    # create directory if not exists
    if not (os.path.isdir(os.path.dirname(get_config_location()))):
        try:
            os.makedirs(os.path.dirname(get_config_location()))
        except:
            print('Error occured while creating config directory')
            return
    
    # open and read
    try:
        with open('data/medusa.json', 'r') as file:
            new_data = file.readlines()
            # open and write
            with open(get_config_location(), 'w') as target:
                target.writelines(new_data)
    except:
        print('Error occured while writing new config')
        return
    
    # print result
    print('Created new Medusa config at', get_config_location())

    # open data
    try:
        with open('data/medusa-data.json', 'r') as file:
            new_data = file.readlines()
            with open(get_data_location(), 'w') as target:
                target.writelines(new_data)
    except:
        print('Error writing new data file')
        return
    
    print('Created new Medusa data at', get_data_location())

def get_config_location():
    return os.path.join(
        appdirs.site_config_dir(APP_NAME, APP_AUTHOR),
        'medusa.json'
    )

def get_data_location():
    return os.path.join(
        appdirs.site_config_dir(APP_NAME, APP_AUTHOR),
        'medusa-data.json'
    )