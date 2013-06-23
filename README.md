# How to build moneyGuru from source

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

(`--system-site-packages` is only required for PyQt and cx_Freeze, so it's not needed on Mac OS X)

Then, you can install pip requirements in your virtualenv:

    $ pip install -r requirements-[osx|win].txt
    
([osx|win] depends, of course, on your platform. On other platforms, just use requirements.txt).

## Alternative: pyvenv

If you're on Python 3.3+, you can use the built-in `pyvenv` instead of `virtualenv`. `pyvenv` is
pretty much the same thing as `virtualenv`, except that it doesn't install distribute and pip, so it
has to be installed manually:

    $ pyvenv --system-site-packages env
    $ source env/bin/activate
    $ curl -O http://python-distribute.org/distribute_setup.py
    $ python distribute_setup.py
    $ easy_install pip

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
