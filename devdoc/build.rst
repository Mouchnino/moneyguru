======================
How to build moneyGuru
======================

Dependencies
============

Before being able to build moneyGuru, a few dependencies have to be installed:

General dependencies
--------------------

- Python 2.6 (http://www.python.org)
- PyYaml, for help files and the build system. (http://pyyaml.org/)
- Nose, to run unit tests. (http://somethingaboutorange.com/mrl/projects/nose/)

OS X prerequisites
------------------

- XCode 3.1 (http://developer.apple.com/TOOLS/xcode/)
- Sparkle (http://sparkle.andymatuschak.org/)
- PyObjC 2.2. (http://pyobjc.sourceforge.net/)
- py2app (http://svn.pythonmac.org/py2app/py2app/trunk/doc/index.html)
  
If you want to build moneyGuru in 64-bit, you'll have to use HS's own forks of py2app, available at http://hg.hardcoded.net/py2app. More details about this at http://www.hardcoded.net/articles/building-64-bit-pyobjc-applications-with-py2app.htm

Windows prerequisites
---------------------

- PyQt 4.6 (http://www.riverbankcomputing.co.uk/news)
- PyInstaller, if you want to build a exe. You don't need it if you just want to run moneyGuru. (http://www.pyinstaller.org/)
- Advanced Installer, if you want to build the installer file. (http://www.advancedinstaller.com/)

Building moneyGuru
==================

First, make sure you meet the dependencies listed in the section above. Then you need to configure your build with::

	python configure.py
	
If you want, you can specify a UI to use with the ``--ui`` option. So, if you want to build moneyGuru with Qt on OS X, then you have to type ``python configure.py --ui=qt``. You can also use the ``--dev`` flag to indicate a dev build (it will build ``mg_cocoa.plugin`` in alias mode).

Then, just build the thing and then run it with::

	python build.py
	python run.py

If you want to create ready-to-upload package, run::

	python package.py