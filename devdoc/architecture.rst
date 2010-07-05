========================
Understanding the source
========================

When looking at a non-trivial codebase for the first time, it's very difficult to understand anything of it until you get the "Big Picture". This page is meant to, hopefully, make you get moneyGuru's big picture.

Model/View/Controller
=====================

moneyGuru tries to follow the MVC pattern. The **View** layer is the platform dependent code (Objective-C code and PyQt code). The role of that code is to be controlled by the **Controllers**, which are located in the ``core.gui`` python package (which is platform independent). The role of the controllers in ``core.gui`` is to "present" the data living in the **Model** (``core.document`` and ``core.model``) to the user.

For example, ``core.gui.account_panel``, when its ``load()`` method is called, checks into its ``Document`` to see which ``Account`` instance (from ``core.model.account``) is selected, then copies relevant information from that ``Account`` instance into its ready-to-be-fetched-by-the-View (on the Cocoa platform, the ``MGAccountProperties`` class) properties.

This method of having multiple GUI codebases is a little unusual. I call this "Cross-Toolkit Software" and I've written `an article about it <http://www.hardcoded.net/articles/cross-toolkit-software.htm>`_.

core.document vs core.model
===========================

To ensure data integrity among model instances, all modifications to any model instance must take place in the ``Document``. For example, ``Transaction.description`` must never be directly set, because if it is, the ``Document`` will not be able to send proper notifications to gui elements that the changes were made.

Therefore, the way ``core.gui`` instances work is that they happily dig directly into models to fetch data, but when comes the time to change anything, they call the corresponding ``Document`` method.

Raw data and Cooked data
========================

You might have noticed that unit with a funny name: ``core.model.oven``. Its role is to "cook" (compute) data from raw data. One example of such cooked data is the running balances (it's not something that is saved in the moneyguru file, but it still has to be displayed by the views). Every time that data changes (through the ``Document``, of course), data has to be re-cooked by the ``Oven``.

Notification System
===================

There are lots of things that can trigger a change in the ``core.gui`` controllers, like data change, date range change, file load, file import, etc.. These changes can very well not have been initiated by the GUI controller that needs to be changed. This is why there's a notification system. The way it works is that GUI controllers all listen to a ``Broadcaster`` (the only broadcasters for now are ``Document`` and ``ImportWindow``). When an event occurs in the broadcaster, the message corresponding to that event is sent to all listeners (GUI controllers), which then act accordingly (usually, they refresh their internal data representation, then tell their own view, the platform-dependant one, to refresh). For example, when ``EntryTable.save_edits()`` is called, ``Document.change_entry()`` is called as well, which makes the ``Document`` broadcast ``transaction_changed``, which is then caught by the chart (if it's visible), which will be refreshed.

Example
=======

Let's use a complete example. Let's see what happens in the code when you press on Show Info on an account, change its name, then press Save. Follow this example through the code, or else you won't understand crap.

When you press Show Info under Cocoa, ``editItemInfo:`` in ``MGMainWindow`` is called. This causes the main window to call its core gui's ``edit_item()``. Because we are currently in an account view, ``self.apanel.load()`` is called with the currently selected account as an argument.

The ``AccountPanel`` loads information relative to that account in its own field (in ``_load()``). After that, ``post_load()`` (this is in ``core.gui.base.Panel``) is called on the view so that it brings up all this information in the GUI.

When the ``NSTextField`` corresponding to the name is changed, nothing happens just yet (at some points, Cocoa binding were used to send values directly to the python side, but it caused problems. I'm trying to phase those out). The new name stays on the Cocoa side. However, when the Save button is clicked and ``MGAccountProperties.saveFields`` is called, the values of all the fields are sent to the ``[self py]`` proxy and then ``AccountPanel.save()`` is called.

This call then causes a call to ``self.document.change_account()``. This will assign the new values to the ``Account`` instance, set a new undo point, re-cook data and broadcast an ``account_changed`` signal.

If you run a search for gui controllers that listen to the ``account_changed`` event, you'll see that ``Chart``, ``ImportWindow`` and ``Report`` listen to that event (by the way, only controllers of visible views actually listen to events). ``Chart`` must be updated in case the currency of the account changed. ``ImportWindow`` must update its list of account targets. ``Report`` (net worth and profit & loss sheets) must be updated because they display account information. If you look at what the ``Report`` does on ``account_changed``, you'll see what most gui controllers do on most events::

    self.refresh()
    self.view.refresh()
    
The first line refreshes the controller's data representation (in this case, accounts organized in a tree) and the second line tells the Cocoa view to refresh itself.