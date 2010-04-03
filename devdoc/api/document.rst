===================================
:mod:`document`
===================================

.. module:: document

.. class:: Document(view, app)

    The ``Document`` is the core class of moneyGuru. It represents a new or opened document and holds all model instances associated to it (accounts, transactions, etc.). The ``Document`` is also responsible for notifying all gui instances of changes. While it's OK for :doc:`GUI instances <gui/index>` to directly access models (through ``Document.transactions`` and ``Document.accounts``, for example), any modification to those models have to go through ``Document``'s public methods.

    Another important role of ``Document`` is to manage selection. Transaction and account selection is shared among gui instances. That is how the :class:`AccountPanel` can know, without holding a reference to the account sheets, which account to load when :meth:`MainWindow.edit_item` is called.
    
    Finally, another important role of the ``Document`` is to manage undo points. For undo to work properly, every mutative action must be properly recorded, and that's what the ``Document`` does.

    .. rubric:: Account-related methods

    .. method:: change_account(account[, name=NOEDIT, type=NOEDIT, currency=NOEDIT, group=NOEDIT, account_number=NOEDIT])

        Sets ``account``'s properties in a proper manner and post a ``account_changed`` notification. Attributes corresponding to arguments set to ``NOEDIT`` will not be touched.

    .. method:: delete_selected_account
    
        Removes the current :attr:`selected_account` from the account list. If the account has entries assigned to it, ``account_needs_reassignment`` will be posted, which makes the account reassignment panel pop up (the panel will then call :meth:`reassign_and_delete_selected_account`).
        
    .. method:: new_account(type, group)
    
        Creates a new account of type ``type`` (an :data:`AccountType`), within the :class:`Group` ``group`` (which can be ``None``). The new account will have a unique name based on the string "New Account" (if it exists, a unique number will be appended to it). Once created, the account is added to the account list, and ``account_added`` is broadcasted.
        
        Returns the created account instance.
    
    .. method:: reassign_and_delete_selected_account(reassign_to)
    
        Reassign all splits having for account :attr:`selected_account` and change their account to ``reassign_to``. After that, it deletes :attr:`selected_account`.
        
    .. method:: toggle_accounts_exclusion(accounts)
    
        Toggles the excluded state (in sheets, when accounts ar grayed out) of ``accounts`` (a ``set`` of :class:`Account`). Afterwards, ``accounts_excluded`` is broadcasted.
    
    .. rubric:: Group-related methods
    
    .. method:: change_group(group[, name=NOEDIT])
    
        Sets ``group``'s properties in a proper manner and post a ``account_changed`` notification. Attributes corresponding to arguments set to ``NOEDIT`` will not be touched.
    
    .. method:: collapse_group(group)
    
        Sets the expanded state of ``group`` to a collapsed state. This state is used by the pie charts to determine if accounts of a group must belong to the same pie slice or not. It is also used during save/load operations so that these states are restored.
    
    .. method:: delete_group(group)
    
        Removes ``group`` from the group list and broadcasts ``account_deleted``. All accounts belonging to the deleted group have their :attr:`Account.group` attribute set to ``None``.
    
    .. method:: expand_group(group)
    
        Sets the expanded state of ``group`` to an expanded state.
        
        .. seealso:: :meth:`collapse_group`
    
    .. method:: new_group(type)
    
        Creates a new group of type ``type`` (an :data:`AccountType`). The new group will have a unique name based on the string "New Group" (if it exists, a unique number will be appended to it). Once created, the group is added to the group list, and ``account_added`` is broadcasted.
    