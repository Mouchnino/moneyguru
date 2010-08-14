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

    .. rubric:: Entry-related methods
    
    .. method:: change_entry(entry[, date=NOEDIT, reconciliation_date=NOEDIT, description=NOEDIT, payee=NOEDIT, checkno=NOEDIT, transfer=NOEDIT, amount=NOEDIT])
    
        Changes the attributes of ``entry`` (and the transaction in which ``entry`` is) to specified values and then post a ``transaction_changed`` notification. Attributes with ``NOEDIT`` values are not touched.
        
        ``transfer`` is the name of the transfer to assign the entry to. If it's not found, a new account will be created.
        
        :param entry: :class:`Entry`
        :param date: ``datetime.date``
        :param reconciliation_date: ``datetime.date``
        :param description: ``str``
        :param payee: ``str``
        :param checkno: ``str``
        :param transfer: ``str``
        :param amount: :class:`Amount`
    
    .. method:: delete_entries(entries)
    
        Remove transactions in which ``entries`` belong from the document's transaction list.
        
        :param entries: list of :class:`Entry`
    
    .. method:: toggle_entries_reconciled(entries)
    
        Toggles the reconciliation flag (sets the ``reconciliation_date`` to the entry's date, or unset it when turning the flag off) of ``entries``.
        
        :param entries: list of :class:`Entry`
    
    .. rubric:: Budget-related methods
    
    .. method:: budgeted_amount_for_target(target, date_range)
    
        Returns the amount budgeted for **all** budgets targeting ``target``. The amount is pro-rated according to ``date_range``.
        
        :param target: :class:`Account`
        :param date_range: :class:`DateRange`

    .. method:: change_budget(original, new)
    
        Changes the attributes of ``original`` so that they match those of ``new``. This is used by the :class:`BudgetPanel`, and ``new`` is originally a copy of ``original`` which has been changed.
        
        :param original: :class:`Budget`
        :param new: :class:`Budget`
    
    .. method:: delete_budgets(budgets)
    
        Removes ``budgets`` from the document.
        
        :param budgets: list of :class:`Budget`
    
    .. rubric:: Schedule-related methods
    
    .. method:: change_schedule(schedule, new_ref, repeat_type, repeat_every, stop_date)
    
        Change attributes of ``schedule``. ``new_ref`` is a reference transaction that the schedule is going to repeat.
        
        :param schedule: :class:`Schedule`
        :param new_ref: :class:`Transaction`
        :param repeat_type: :const:`RepeatType`
        :param stop_date: ``datetime.date``
    
    .. method:: delete_schedules(schedules)
    
        Removes ``schedules`` from the document.
        
        :param schedules: list of :class:`Schedule`
    
    .. rubric:: Load/Save/Import methods
    
    .. method:: adjust_example_file()
    
        Adjusts all document's transactions so that they become current. This is used when loading the example document so that it's not necessary to do it manually.
    
    .. method:: clear()
    
        Removes all data from the document (transactions, accounts, schedules, etc.).
    
    .. method:: load_from_xml(filename)
    
        Clears the document and loads data from ``filename``, which must be a path to a moneyGuru XML document.
        
        :param filename: ``str``
    
    .. method:: save_to_xml(filename[, autosave=False])
    
        Saves the document to ``filename`` in moneyGuru's XML document format. If ``autosave`` is true, the operation will not affect the document's modified state and will not make editing stop, if editing there is (like it normally does without the autosave flag to make sure that the input being currently done by the user is saved).
        
        :param filename: ``str``
        :param autosave: ``bool``
    
    .. method:: save_to_qif(filename)
    
        Saves the document to ``filename`` in the QIF format.
        
        :param filename: ``str``
    
    .. method:: parse_file_for_import(filename)
    
        Opens and parses ``filename`` and try to determine its format by successively trying to read is as a moneyGuru file, an OFX, a QIF and finally a CSV. Once parsed, take the appropriate action for the file which is either to show the CSV options window or to call :meth:`load_parsed_file_for_import`
        
    .. method:: load_parsed_file_for_import()
    
        When the document's ``loader`` has finished parsing (either after having done CSV configuration or directly after :meth:`parse_file_for_import`), call this method to load the parsed data into model instances, ready to be shown in the Import window.
    
    .. method:: import_entries(target_account, ref_account, matches)
    
        Imports entries in ``mathes`` into ``target_account``. ``target_account`` can be either an existing account in the document or not. ``ref_account`` is a reference to the temporary :class:`Account` created by the loader.
        
        ``matches`` is a list of tuples ``(entry, ref)`` with ``entry`` being the entry being imported and ``ref`` being an existing entry in the ``target_account`` bound to ``entry``. ``ref`` can be ``None`` and it's only possible to have a ``ref`` side when the target account already exists in the document.
        
    .. method:: is_dirty()
    
        Returns whether the document has been modified since the last time it was saved.
    
    .. rubric:: Date Range
    
    .. method:: select_month_range(starting_point)
    .. method:: select_quarter_range(starting_point)
    .. method:: select_year_range(starting_point)
    .. method:: select_year_to_date_range()
    .. method:: select_running_year_range()
    .. method:: select_all_transactions_range()
    
        Sets the document's date range to the date range corresponding to the method called. For navigable date ranges, a ``starting_point`` has to be given, which can be either a date or a date range. The resulting date range will contain the starting point (or its start date, if it's a date range).
        
    .. method:: select_custom_date_range([start_date, end_date])
    
        Sets the document's date range to a range with arbirtrary start and end dates. If these dates are not given, the document will send a notification for the custom date range panel to show up.
        
    .. method:: select_prev_date_range()
    .. method:: select_next_date_range()
    
        If the current date range is navigable, select the date range coming before/after the current one.
    
    .. method:: select_today_date_range()
    
        If the current date range is navigable, select a date range that contains today's date.
    
    .. attribute:: date_range
    
        The currently selected date range for the document.
    
    .. rubric:: Undo/Redo
    
    .. method:: can_undo()
    .. method:: can_redo()
    
        Returns wether the document has something to undo or redo.
    
    .. method:: undo_description()
    .. method:: redo_description()
    
        Returns a string describing the action that would be undone or redone if :meth:`undo` or :meth:`redo` was called.
    
    .. method:: undo()
    
        Undo the last undoable action.
    
    .. method:: redo()
    
        Redo the last undone action.
    
    .. rubric:: Misc
    
    .. method:: close()
    
        Saves preferences and tells GUI elements about the document closing (so that they can save their own preferences if needed).
    
    .. method:: stop_edition()
    
        Tells GUI elements to stop editing. Some actions create glitches if they are done while a table/outline is being edited, so it's necessary to stop editing before that action is done.
    
    .. attribute:: filter_string
    
        When set to an non empty string, it restricts visible transactions/entries in :class:`TransactionTable` and :class:`EntryTable` to those matching with the string.
    
    .. attribute:: filter_type
    
        When set to something else than ``None``, it restricts visible transactions in :class:`TransactionTable` and :class:`EntryTable` to those matching the :data:`FilterType` set.
    
.. data:: FilterType

    A class in which available filter constants are defined: ``Unassigned``, ``Income``, ``Expense``, ``Transfer``, ``Reconciled`` and ``NotReconciled``.