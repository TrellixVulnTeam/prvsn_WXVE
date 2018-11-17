Prvsn
=================

`prvsn` is a simple provisioning tool.

[![Build](https://travis-ci.com/acoomans/prvsn.svg?branch=master)](https://travis-ci.org/acoomans/prvsn)
[![Pypi version](http://img.shields.io/pypi/v/prvsn.svg)](https://pypi.python.org/pypi/prvsn)
[![Pypi license](http://img.shields.io/pypi/l/prvsn.svg)](https://pypi.python.org/pypi/prvsn)
![Python 2](http://img.shields.io/badge/python-2-blue.svg)
![Python 3](http://img.shields.io/badge/python-3-blue.svg)

## Usage

### Install

	python setup.py install

### Developing

	python setup.py develop
	python setup.py develop --uninstall

### Running tests

	python setup.py test

	
## Objectives

### Goals

Easy for quickly setup a machine for hacking:

- easy to provision a single machine
- works in python
- simple way to
    - add a file, possibly a template
    - install package
    - run a command in bash
- works out of the box:
    - python 2.7 & 3 compatibility
    - no external dependencies

### Non-Goals

Large scale provisioning:

- provision thousands or more machines
- strict dependencies, complex dependency graph
- external recipes/supermaket support

If those are your goals, have looks at Puppet or Chef or others.


## Manual

### Hierarchy

Configurations are called `roles` and are grouped into a `runbook`.

The file hierarchy looks like:

	runbook
	|- roles
	   |- web
	   |- ...
	   |- desktop
	      |- main.py
	      |- files


- `main.py` is the main python entry point
- `files` is to contain any files you want to use

### Tasks

A role's `main.py` can contain one or more `tasks` (also called `states` since they're mostly descriptive).

Common task options include:

- `secure`: no output will be shown on console nor logs.


#### Command Tasks

`command(interpreter, cmd)`

`bash(cmd)`:

Runs some code in bash. Hopefully this is never needed.

	bash('''
	echo "hello"
	ls
	ps
	''')

`bash(cmd)`

Runs some code in ruby.


#### File Tasks

`file(source, file, replacements={})`:

source can either be a URL or a file's path relative to the role's `files` directory.

	file('asound.conf', '/etc/asound.conf')
	
	file(
	    'http://example.com/asound.conf', 
	    '/etc/asound.conf'
	)

replacements rules can be specified, so the file acts as a template.

	file(
		'resolv.conf', 
		'/etc/resolv.conf',
		{
		    'IPADDRESS': '192.168.0.1'
		}
	)

#### Kernel Tasks

`module(name)` (linux only):

	module('v4l')

#### Package Tasks

`package`:

Should automatically detect the package manager in presence. 
If multiple ones are present, it is possible to explicitly specify which to use:

`homebrew_package`

`apt_package`

`yum_package`

	package('vim')
	
	      