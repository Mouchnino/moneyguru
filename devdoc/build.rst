======================
How to build moneyGuru
======================

Dependencies
============

Before being able to build moneyGuru, a few dependencies have to be installed:

General dependencies
--------------------

- Python 3.1 (http://www.python.org)
- hsutil3k 1.0.1 (http://hg.hardcoded.net/hsutil)
- sgmllib3k (http://bitbucket.org/hsoft/sgmllib)
- PyYaml, for help files and the build system. (http://pyyaml.org/)
- Markdown, for help files. (http://www.freewisdom.org/projects/python-markdown/)
- py.test, to run unit tests. (http://codespeak.net/py/dist/test/)

OS X prerequisites
------------------

- XCode 3.1 (http://developer.apple.com/TOOLS/xcode/)
- Sparkle (http://sparkle.andymatuschak.org/)
- PyObjC 2.3. (http://pyobjc.sourceforge.net/)
- py2app 0.5.4 (http://bitbucket.org/ronaldoussoren/py2app)
  
Windows prerequisites
---------------------

- PyQt 4.7.5 (http://www.riverbankcomputing.co.uk/news)
- cx_Freeze, if you want to build a exe. You don't need it if you just want to run moneyGuru. (http://cx-freeze.sourceforge.net/)
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