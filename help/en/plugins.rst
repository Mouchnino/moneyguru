Plugins
=======

Since moneyGuru v2.5, it's possible to expand moneyGuru's capability through Python plugins. Plugins
are Python 3 source files located in the plugin folder (the location of that folder depends on the
system, but you can open that folder through "File --> Open Plugin Folder"). When moneyGuru
launches, it looks in that folder for plugins to load and for each plugin it finds, it will add an
item to the plugin list located in the "New Tab" view. To open a plugin, simply double-click on the
name of that plugin in the list.

To install a plugin, take the Python file (a ``.py`` file), put it in the plugin folder and
restart moneyGuru.

**Warning.** moneyGuru plugins are not sandboxed, which means that technically, they could contain
malicious code. Only install plugins from trusted sources or after having reviewed the code yourself.

Limitations
-----------

First things first, the plugin feature is brand new, so there are many rough edges and limitations.
For the first iteration of the feature, the plugin is limited to a single read-only table. The data
in the table is not "live" data and thus isn't refreshed when data in the document changes, so the
tab has to be closed and reopened for the data to be refreshed.

But despite those limitations, there's quite a lot of possibilities, especially for custom reports.
Printing, sorting and CSV-copy-pasting (selecting rows, copying data and then pasting it in
Excel/Numbers) work with those tables.

Creating a plugin
-----------------

Other than `a small convenience API <http://bitbucket.org/hsoft/moneyguru/src/tip/core/plugin.py>`_,
there's no "plugin" API, you're coding straight on top of moneyGuru's code. Developer documention
for moneyGuru's code is unfortunately not very extensive, but I've created a few well commented
plugin examples and I think that they're your best starting point.

So, to create a plugin, I'd suggest that you take one of the examples (they're automatically copied
in your plugin folder. You can also find the latest version of these examples
`on Bitbucket <http://bitbucket.org/hsoft/moneyguru/src/tip/plugin_examples>`_), duplicate it and
try to wade your way through with example comments. There's a
`developer documentation <http://www.hardcoded.net/docs/moneyguru>`_ but it's far from complete.
Looking at moneyGuru's `source code <http://bitbucket.org/hsoft/moneyguru>`_ is also a good way
to learn how to work with it, but understanding it can be quite an undertaking.

I'm very interested in knowing about plugin development efforts so don't hesitate to
`contact me <mailto:hsoft@hardcoded.net>`_ if you need help with the development of your plugin.
