TS3CLI [![Build Status](https://travis-ci.org/Thor77/TS3CLI.svg?branch=master)](https://travis-ci.org/Thor77/TS3CLI) [![PyPI](https://img.shields.io/pypi/v/ts3cli.svg)](https://pypi.python.org/pypi/ts3cli)
======

A CLI for the Teamspeak3 query interface for easy server administration.

Installation
============
* Clone this repo and `python setup.py install`
* Install from PyPi `pip install ts3cli`

Usage
=====
```
Usage: ts3cli [OPTIONS] COMMAND [ARGS]...

Options:
  --host TEXT      teamspeak query host
  --port INTEGER   teamspeak query port
  --username TEXT  query username
  --password TEXT  query password  [required]
  --help           Show this message and exit.

Commands:
  ban              Ban a client
  bandel           Remove a ban
  banlist          List bans
  channel          List channel on a virtual server
  channelcreate    Create a channel
  channelinfo      View detailed information about a channel
  clientinfo       View detailed information about a client
  clients          List clients on a virtual server
  complaintdel     Delete a complaint
  complaintdelall  Delete all complaints for a specific client
  complaints       List complaints
  gm               Send a global message
  kick             Kick a client
  move             Move a client to another channel
  poke             Poke a client
  server           List virtual servers
  servercreate     Create a new virtual server
  serverdelete     Delete a virtual server
  serverstart      Start a server
  serverstop       Stop a server
```
