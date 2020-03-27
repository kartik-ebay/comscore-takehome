# Comscore Coding Exercise [![Build Status](https://travis-ci.org/manoflogan/comscore-takehome.svg?branch=master)](https://travis-ci.org/manoflogan/comscore-takehome)

### Table of Contents

- [Assignment](Assignment.md)
- [Requirements](#requirements)
- [Setup](#setup)
- [Execution](#execution)
- [Overview](#overview)

### Requirements

* Python 3.8.x and above

### Setup

* Install Python 3.8.x and above. You can use your favourite tool to install the software (HomeBrew, pyenv) etc.

* Set up virtualenv with the following command ``virtualenv -p `which python3` env``. Activate the virtual environment using the command `source env/bin/activate`

* Install `pipenv` using the command `pip install pipenv`

* Install the required project dependencies within the virtual environment with the command `pipenv install`

* Run the command `pytest` to run the unit tests. The code coverage reports will generated and displayed on the console.

## Execution

* Run the command `python datastore_importer.py < file.txt` or `python datastore_importer.py file.txt` to execute the program.

* Run the command `./query.sh <arguments>` to run the query module.

## Overview

The implementation uses a file on disk to represent the stored data. All filter operations are performed on the contents of the file read from disk.

I chose Python to implement the assignment because Python 3's [fileinput API](https://docs.python.org/3/library/fileinput.html) can read from both input file if as a command line argument, but can also default to standard input without any change in code. In addition, Python ecosystem supports all the tools and libraries required to write good quality code in that language.
