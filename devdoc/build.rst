======================
How to build moneyGuru
======================

Dependencies
============

Before being able to build moneyGuru, a few dependencies have to be installed:

General dependencies
--------------------

- Python 3.1 (3.2 on Mac OS X) (http://www.python.org)
- sgmllib3k (http://bitbucket.org/hsoft/sgmllib)
- Sphinx 1.0.6 (http://sphinx.pocoo.org/)
- pytest 2.0.0, to run unit tests. (http://pytest.org/)
- pytest-monkeyplus, a pytest plugin. (http://bitbucket.org/hsoft/pytest-monkeyplus)

OS X prerequisites
------------------

- XCode 3.1 (http://developer.apple.com/TOOLS/xcode/)
- Sparkle (http://sparkle.andymatuschak.org/)
- PyObjC 2.3. (http://pyobjc.sourceforge.net/)
- pluginbuilder 1.0.0 (http://bitbucket.org/hsoft/pluginbuilder)
  
Windows prerequisites
---------------------

- PyQt 4.7.5 (http://www.riverbankcomputing.co.uk/news)
- cx_Freeze, if you want to build a exe. You don't need it if you just want to run moneyGuru. (http://cx-freeze.sourceforge.net/)
- Advanced Installer, if you want to build the installer file. (http://www.advancedinstaller.com/)

Prerequisite gotchas
--------------------

Correctly installing the prerequisites is tricky. Make sure you have at least the version number 
required for each prerequisite.

If you didn't use mercurial to download this source, you probably have an incomplete source folder!
External projects (hscommon, qtlib, cocoalib) need to be at the root of the moneyGuru project 
folder. You'll have to download those separately. Or use mercurial, it's much easier.

As far as I can tell, you don't *have* to compile/install everything manually and you can normally
use ``easy_install`` to install python dependencies. However, be aware that compiling/installing
manually from the repositories of each project is what I personally do, so if you hit a snag 
somewhere, you might want to try the manual way.

PyObjC's website is badly outdated. Also, as far as I can tell, the package installable with
``easy_install`` has good chances of not working. Your best bet is to download the latest tagged
version from the repository and compile it from source.

Also, on OS X, don't try to use the built-in python 2.x to install Sphinx on (the only pre-requisite
that doesn't run on python 3 yet). There's some weird error popping up when moneyGuru tries to build 
its help file. Install your own framework version of python 2.7, and then install Sphinx on that. 
When Sphinx supports Python 3, things will be easier because you'll be able to install sphinx on the 
same Python version you build moneyGuru with.

Another one on OS X: I wouldn't use macports/fink/whatever. Whenever I tried using those, I always 
ended up with problems.

Also, I don't know yet if it's possible to compile moneyGuru with XCode 4, I haven't tried it yet.
It's safer to use XCode 3.x. However, I don't see why it wouldn't work, so it very well might work.

Whenever you have a problem, always double-check that you're running the correct python version. 
You'll probably have to tweak your $PATH.

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