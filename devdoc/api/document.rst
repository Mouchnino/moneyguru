===================================
:mod:`document`
===================================

.. module:: document

.. class:: Document(view, app)

    The ``Document`` is the core class of moneyGuru. It represents a new or opened document and holds all model instances associated to it (accounts, transactions, etc.). The ``Document`` is also responsible for notifying all gui instances of changes. While it's OK for :doc:`GUI instances <gui/index>` to directly access models (through ``Document.transactions`` and ``Document.accounts``, for example), any modification to those models have to go through ``Document``'s public methods.
    
    Another important role of ``Document`` is to manage selection. Transaction and account selection is shared among gui instances. That is how the :class:`AccountPanel` can know, without holding a reference to the account sheets, which account to load when :meth:`MainWindow.edit_item` is called.