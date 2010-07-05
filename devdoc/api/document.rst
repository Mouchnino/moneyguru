===================================
The Document class
===================================

.. module:: document

.. class:: Document(view, app)

    The ``Document`` is the core class of moneyGuru. It represents a new or opened document and holds all model instances associated to it (accounts, transactions, etc.). The ``Document`` is also responsible for notifying all gui instances of changes. While it's OK for :doc:`GUI instances <gui/index>` to directly access models (through ``Document.transactions`` and ``Document.accounts``, for example), any modification to those models have to go through ``Document``'s public methods.

    Another important role of the ``Document`` is to manage undo points. For undo to work properly, every mutative action must be properly recorded, and that's what the ``Document`` does.

    When calling methods that take "hard values" (dates, descriptions, etc..), it is expected that these values have already been parsed (it's the role of the GUI instances to parse data). So dates are ``datetime.date`` instances, amounts are :class:`Amount` instances, indexes are ``int``.
    
    .. rubric:: Account-related methods

    .. method:: change_account(account[, name=NOEDIT, type=NOEDIT, currency=NOEDIT, group=NOEDIT, account_number=NOEDIT])

        Sets ``account``'s properties in a proper manner and post a ``account_changed`` notification. Attributes corresponding to arguments set to ``NOEDIT`` will not be touched.
        
        :param account: :class:`Account`
        :param name: ``str``
        :param type: :data:`AccountType`
        :param currency: :class:`Currency`
        :param group: :class:`Group`
        :param account_number: ``str``
    
    .. method:: delete_selected_account
    
        Removes the current :attr:`selected_account` from the account list. If the account has entries assigned to it, ``account_needs_reassignment`` will be posted, which makes the account reassignment panel pop up (the panel will then call :meth:`reassign_and_delete_selected_account`).
        
    .. method:: new_account(type, group)
    
        Creates a new account of type ``type``, within the ``group`` (which can be ``None``). The new account will have a unique name based on the string "New Account" (if it exists, a unique number will be appended to it). Once created, the account is added to the account list, and ``account_added`` is broadcasted.
        
        :param type: :data:`AccountType`
        :param group: :class:`Group`
        :rtype: :class:`Account`
    
    .. method:: toggle_accounts_exclusion(accounts)
    
        Toggles the excluded state (in sheets, when accounts ar grayed out) of ``accounts``. Afterwards, ``accounts_excluded`` is broadcasted.
        
        :param accounts: a ``set`` of :class:`Account`
    
    .. rubric:: Group-related methods
    
    .. method:: change_group(group[, name=NOEDIT])
    
        Sets ``group``'s properties in a proper manner and post a ``account_changed`` notification. Attributes corresponding to arguments set to ``NOEDIT`` will not be touched.
        
        :param group: :class:`Group`
        :param name: ``str``
    
    .. method:: delete_group(group)
    
        Removes ``group`` from the group list and broadcasts ``account_deleted``. All accounts belonging to the deleted group have their :attr:`Account.group` attribute set to ``None``.
        
        :param group: :class:`Group`
    
    .. method:: new_group(type)
    
        Creates a new group of type ``type`` (an :data:`AccountType`). The new group will have a unique name based on the string "New Group" (if it exists, a unique number will be appended to it). Once created, the group is added to the group list, and ``account_added`` is broadcasted.
        
        :param type: :data:`AccountType`
        :rtype: :class:`Group`
    
    .. rubric:: Transaction-related methods
    
    .. method:: can_move_transactions(transactions, before, after)
    
        Returns whether ``transactions`` can be be moved (re-ordered). Transactions can only be moved when all transactions are of the same date, and that the date of those transaction is between the date of ``before`` and ``after``. When ``before`` or ``after`` is ``None``, it means that it's the end or beginning of the list.
        
        :param transactions: a collection of :class:`Transaction`
        :param before: :class:`Transaction`
        :param after: :class:`Transaction`
        :rtype: ``bool``
    
    .. method:: change_transaction(original, new)
    
        Changes the attributes of ``original`` so that they match those of ``new``. This is used by the :class:`TransactionPanel`, and ``new`` is originally a copy of ``original`` which has been changed. Accounts linked to splits in ``new`` don't have to be accounts that are part of the document. This method will automatically internalize accounts linked to splits (and create new accounts if necessary).
        
        If ``new``'s date is outside of the current date range, the date range will automatically be changed so that it contains ``new``.
        
        If ``original`` is a schedule :class:`Spawn`, the UI will be queried for a scope, which might result in the change being aborted.
        
        After the transaction change, ``transaction_changed`` is broadcasted.
        
        :param original: :class:`Transaction`
        :param new: :class:`Transaction`
    
    .. method:: change_transactions(transactions[, date=NOEDIT, description=NOEDIT, payee=NOEDIT, checkno=NOEDIT, from_=NOEDIT, to=NOEDIT, amount=NOEDIT, currency=NOEDIT])
    
        Changes the attributes of every transaction in ``transactions`` to the values specified in the arguments (arguments left to ``NOEDIT`` have no effect).
        
        ``from_`` and ``to`` are account **names** rather than being :class:`Account` instances. If the names don't exist, they'll automatically be created.
        
        If any transaction in ``transactions`` is a schedule :class:`Spawn`, the UI will be queried for a scope, which might result in the change being aborted.
        
        After the transaction change, ``transaction_changed`` is broadcasted.
        
        :param date: ``datetime.date``
        :param description: ``str``
        :param payee: ``str``
        :param checkno: ``str``
        :param from_: ``str``
        :param to: ``str``
        :param amount: :class:`Amount`
        :param currency: :class:`Currency`
    
    .. method:: delete_transactions(transactions)
    
        Removes every transaction in ``transactions`` from the document.
        
        If any transaction in ``transactions`` is a schedule :class:`Spawn`, the UI will be queried for a scope, which might result in the deletion being aborted.
        
        After the transaction deletion, ``transaction_deleted`` is broadcasted.
        
        :param transactions: a collection of :class:`Transaction`
    
    .. method:: duplicate_transactions(transactions)
    
        For each transaction in ``transactions``, add a new transaction with the same attributes to the document.
        
        After the operation, ``transaction_changed`` is broadcasted.
        
        :param transactions: a collection of :class:`Transaction`
        
    .. method:: move_transactions(transactions, to_transaction)
    
        Re-orders ``transactions`` so that they are right before ``to_transaction``. If ``to_transaction`` is ``None``, it means that we move transactions at the end of the list.
        
        Make sure your move is legal by calling :meth:`can_move_transactions` first.
        
        After the move, ``transaction_changed`` is broadcasted.
        
        :param transactions: a collection of :class:`Transaction`
        :param to_transaction: :class:`Transaction`
