# Medusa
## A Python program for managing multiple Minecraft servers

[![pipeline status](https://git.therode.net/jrode/medusa/badges/main/pipeline.svg)](https://git.therode.net/jrode/medusa/-/commits/main)
[![coverage report](https://git.therode.net/jrode/medusa/badges/main/coverage.svg)](https://git.therode.net/jrode/medusa/-/commits/main)

Medusa provides tools capable of managing multiple Minecraft servers, ranging from linking whitelist files updating Spigot and plugin installations.

## Overview
Medusa runs on the same machine hosting the Minecraft servers. This allows it to work with the filesystem to manage server files and to start up the game servers. Once the servers are running, Medusa communicates with them over RCON.

## Installing

## Usage
After installing, Medusa needs some basic configuration. You can configure Medusa by directly editing `medusa.json` or by entering indivudal `config set` commands.


```
medusa config set server_directory /path/to/servers
```
The above command informs the program that the Minecraft servers are stored in the `/path/to/servers` directory. All `config set` commands commit changes to the config on-disk.

By default, the config is stored with the application at `data/medusa.json`. If you want to load the config file from elsewhere, you'll have to symlink it yourself.

Then execute a scan.
```
medusa server scan
```

This will check the server directory for any unregistered servers. The scan looks for a top-level file called `.medusa` in each server directory. If the *dotmedusa* file does not exist, then the program checks to see if it has already registered a server with the same full path. If it hasn't already registered this path before, then the program writes a basic *dotmedusa* file and appends its config with the new entry.