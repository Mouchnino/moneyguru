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

moneyGuru can be built with XCode 4, but there's gotchas, see below.
  
Windows prerequisites
---------------------

- PyQt 4.7.5 (http://www.riverbankcomputing.co.uk/news)
- cx_Freeze, if you want to build a exe. You don't need it if you just want to run moneyGuru. (http://cx-freeze.sourceforge.net/)
- Advanced Installer, if you want to build the installer file. (http://www.advancedinstaller.com/)

The easy way!
-------------

There's an easy way to install the majority of the prerequisites above, and it's `pip <http://www.pip-installer.org/>`_ which has recently started to support Python 3. So install it and then run::

    pip install -r requirements-[osx|win|lnx].txt

([osx|win|lnx] depends, of course, on your platform). Because Sphinx doesn't support Python 3 yet, it's not in the requirements file and you'll have to install it manually. You might have to compile PyObjC manually too (see gotchas below). Sparkle and Advanced Installer, having nothing to do with Python, are also manual installs.

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

moneyGuru can be built with XCode 4 (until support for 10.5 is dropped, xcode 3 and xcode 4 projects
have to be maintained in parallel though). You build it through `build.py`, like you'd normally do,
but make sure that you installed the latest version of macholib because there was a
10.7 related bug that was fixed recently. Right now, the fix hasn't even been released yet so you 
have to install directly from the repo ( http://bitbucket.org/ronaldoussoren/macholib ). The fix
in question is at http://bitbucket.org/ronaldoussoren/macholib/changeset/4ab0de0f5b60

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