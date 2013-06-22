# How to build moneyGuru from source

## Submodule checkout

The first thing to do after a fresh clone from git is to ensure that your submodules are checkout
out, that that is done with:

    $ git submodule init
    $ git submodule update

## Prerequisites installation

Then, you have to make sure that your system has to "non-pip-installable" prerequisites installed:

* All systems: Python 3.2+
* Mac OS X: The last XCode to have the 10.6 SDK included.
* Windows: Visual Studio 2008, PyQt 4.7+, cx_Freeze and Advanced Installer

On Ubuntu, the apt-get command to install all pre-requisites is:

    $ apt-get install python3-dev python3-pyqt4 pyqt4-dev-tools python3-setuptools

## Virtualenv setup

First, you need `pip` and `virtualenv` in your system Python install:

    $ sudo easy_install pip
    $ sudo pip install virtualenv

Then, in moneyGuru's source folder, create a virtual environment and activate it:

    $ virtualenv --system-site-packages env
    $ source env/bin/activate

Then, you can install pip requirements in your virtualenv:

    $ pip install -r requirements-[osx|win].txt
    
([osx|win] depends, of course, on your platform. On other platforms, just use requirements.txt).

## Actual building and running

With your virtualenv activated, you can build and run moneyGuru with these commands:

    $ python configure.py
    $ python build.py
    $ python run.py

You can also package moneyGuru into an installable package with:
    
    $ python package.py

# Further documentation

There's a more complete development documention in 'devdoc'. This documentation has to be built
using Sphinx (http://sphinx.pocoo.org/). There's also an online version of this documentation at
http://www.hardcoded.net/docs/moneyguru/.
