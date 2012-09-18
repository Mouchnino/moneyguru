======================
How to build moneyGuru
======================

Dependencies
============

Before being able to build moneyGuru, a few dependencies have to be installed:

General dependencies
--------------------

- Python 3.2 (http://www.python.org)
- sgmllib3k (http://bitbucket.org/hsoft/sgmllib)
- Sphinx 1.1.2 (http://sphinx.pocoo.org/)
- polib 0.7.0 (http://bitbucket.org/izi/polib)
- pytest 2.0.0, to run unit tests. (http://pytest.org/)
- pytest-monkeyplus, a pytest plugin. (http://bitbucket.org/hsoft/pytest-monkeyplus)

OS X prerequisites
------------------

- XCode 4.2's command line tools
- objp 1.2.0 (https://bitbucket.org/hsoft/objp)
- xibless 0.5.0 (https://bitbucket.org/hsoft/xibless)

Windows prerequisites
---------------------

- PyQt 4.7.5 (http://www.riverbankcomputing.co.uk/news)
- cx_Freeze, if you want to build a exe. You don't need it if you just want to run moneyGuru. (http://cx-freeze.sourceforge.net/)
- Advanced Installer, if you want to build the installer file. (http://www.advancedinstaller.com/)

The easy way!
-------------

There's an easy way to install the majority of the prerequisites above, and it's `pip <http://www.pip-installer.org/>`_ which has recently started to support Python 3. So install it and then run::

    pip install -r requirements-[osx|win].txt

[osx|win] depends on your platform. On Linux, run the base requirements file, requirements.txt.
Sparkle and Advanced Installer, having nothing to do with Python, have to be manually installed.

PyQt isn't in the requirements file either (there's no package uploaded on PyPI) and you also have
to install it manually.

Gotchas
-------

If you didn't use mercurial to download this source, you probably have an incomplete source folder!
External projects (hscommon, qtlib, cocoalib) need to be at the root of the moneyGuru project 
folder. You'll have to download those separately. Or use mercurial, it's much easier.

Whenever you have a problem, always double-check that you're running the correct python version. 
You'll probably have to tweak your $PATH.

Building moneyGuru
==================

First, make sure you meet the dependencies listed in the section above. Then you need to configure your build with::

	python configure.py
	
If you want, you can specify a UI to use with the ``--ui`` option. So, if you want to build moneyGuru with Qt on OS X, then you have to type ``python configure.py --ui=qt``. You can also use the ``--dev`` flag to indicate a dev build.

Then, just build the thing and then run it with::

	python build.py
	python run.py

If you want to create ready-to-upload package, run::

	python package.py