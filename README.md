TS3CLI [![Build Status](https://travis-ci.org/Thor77/TS3CLI.svg?branch=master)](https://travis-ci.org/Thor77/TS3CLI)
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
  --username TEXT  query username  [required]
  --password TEXT  query password  [required]
  --help           Show this message and exit.

Commands:
  client   View detailed information about a client
  clients  List clients on a virtual server
  gm       Send a global message
  poke     Poke a client
  server   List virtual servers
```
