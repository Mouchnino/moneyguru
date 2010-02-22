<%!
	title = 'Editing a moneyGuru document'
	selected_menu_item = 'editing'
%>
<%inherit file="/base_mg.mako"/>

The Basics
-----

There are a few keystrokes and clicks that work the same way for everything in moneyGuru. First, there is this set of 3 buttons at the bottom left corner:

![](images/edition_buttons.png)

The + button creates a new thing, the - button removes the selected thing and the "i" button shows info about the selected thing. The "thing" depends on the current view. In the Balance Sheet and the Income Statement, it is an account. In the Transactions and Account views, it is a transaction. Also, if you select more than one transaction and click on the "i" button, the Mass Edition panel will show up rather than the transaction details panel.

Of course, it's also possible to do the same thing with the keyboard. ${cmd}N creates a new thing, Delete or Backspace remove the selected thing and ${cmd}I shows info about the selected thing.

It's possible to edit things by double clicking on a cell that is editable (for example, the name cell of an account). It is also possible to start editing a thing by selecting it and pressing Return. The first editable cell will be in edit mode.

When in edit mode, Tab and Shift-Tab can be used to navigate editable cells. When there is no more editable cell in a row, edition ends. It's also possible to end edition by pressing Return again. You can cancel edition by pressing Escape. When doing so, everything you edited in the currently edited row will be reverted to its old value.

Accounts
-----

Accounts are edited from the Balance Sheet and the Income Statement. When you create a new account, it will be created under the type of account that currently contains the selection. For example, if I have "Credit Card" selected and press ${cmd}N, a new liability will be created. New accounts are automatically created in edition mode. Type a new name then press Return to end edition.

You can also use drag & drop to change an account type or group (yeah, account group. use ${cmd_shift}N to create one).

![](images/edition_account_panel.png)

Using Show Info on an account will bring the account edition panel shown above. From there, you can edit an account name, but also change its type, its [currency](currencies.htm) and its account number. An account number is a numerical reference to an account. Use this if your accounting has account number (you know, 1000-1999 is for assets, 8000-8999 is for expenses, stuff like that). When an account has an account number, that number will be displayed along with the name in the Transaction and Account views. Moreover, you can type the number instead of the name to reference to that account (if you know the numbers by heart, it will make typing much faster).

Little aside note: Changing an account's currency does **not** change the currency of the transactions it contains.

Transactions
-----

Transactions are edited from the Transactions and Account views. When creating a new transaction, the date of the previously selected transaction will be used as the new transaction's date (speaking of which, see the "Date Editing" section below). The Description, Payee and Account (From, To Transfer) columns are auto-completed. This means that as soon as you type something in them, moneyGuru will look in the other transactions and give you a completion proposition. You can cycle through the propositions with the up and down arrows. To accept a proposition, just tab out. You can also, of course, just continue to type.

It's possible to re-order a transaction within other transactions of the same date. To do so, you can use drag & drop, or you can use ${cmd}+ and ${cmd}-.

If you type the name of an account that doesn't exist in an Account column, this account will automatically be created as an income or expense account (depending on the amount of the transaction). Don't worry about typos creating tons of accounts that you'll have to clean up. If you fix a typo in a transaction, the automatically created account will automatically be removed.

![](images/edition_transaction_panel.png)

Using Show Info on a single transaction brings the panel above up. With it, you can edit everything that you can edit from the Transactions and Account views, and additionally, you can create and edit transaction with more than 2 entries (commonly called a "Split Transaction") with the table at the bottom. To do so, select the "Splits" tab.

![](images/edition_transaction_panel_split.png)

From this tab, you can add new splits to your transactions. When you add splits, the transaction constantly balances itself automatically. The rules for split balancing are a little complex (see "Transaction balancing" below), but using the split table is usually very simple. For example, to re-create the transaction shown in the picture above, you'd do the following:

1. Create a new transaction through the Transaction or Account table that transfers 1200$ from Salary to Checking.
1. Click the Show Info button and select the Splits tab.
1. Add a new split with the + button.
1. Write down "Federal Taxes" in the Account column and "126.12" in the Debit column.
1. Add a new split with the + button.
1. Write down "State Taxes" in the Account column and "287.92" in the Debit column.

You'll notice that adding new splits automatically deduces the amount assigned to Checking.

![](images/edition_mass_edition_panel.png)

Using Show Info with more than one transaction selected bring up the panel above. It allows you to perform mass editing. When you press on Save, all selected transactions will have the attributes that have the checkboxes next to them checked changed to the value of the field next to it.

Date Editing
-----

Whenever a date is edited, it is edited using a special widget. This widget has 3 fields: day, month and year. Whenever an editing is initiated, it is always the **day** fields that starts out selected, whatever your date format is. You can navigate the fields with the left and right arrows. You can increment and decrement the currently selected field with the up and down arrows. You can of course type the date out. The widget automatically changes the selection when a date separator is typed or the maximum length of a field is reached. Here is a list of the rules that this widget follows, just to make it clear:

* The display format is always your system's format.
* The **input** format is always day --> month --> year.
* Whatever your system date format is, you can type a date by padding your values with 0. For example, even if your date format is mm/dd/yy, you can enter the date "07/06/08" by typing "060708".
* Whatever your system date format is, you can type a date by using separators. For example, even if your date format is yyyy-mm-dd, you can type "2008-07-06" by typing "6-7-08"

While editing a transaction or entry, if you set the date to something outside the current date range, you will get a ![](images/backward_16.png) or a ![](images/forward_16.png) showing up. This means that if your date range is "navigable" (Month, Quarter, Year), that date range will be adjusted when editing ends to continue to show the edited transaction. If your current date range is not "navigable" (Year to date, Running year, Custom), the transaction will disappear from the current view when editing ends.

Transaction Balancing
-----

Because moneyGuru follows double-entry accounting, splits in a transaction must always balance. To make moneyGuru easier to use, this balancing happens automatically and follow a couple of rules.

* The Amount field of a transaction represents the sum of amounts on each side (debit side and credit side).
* Most of the time, when moneyGuru balances splits, it tries to keep the Amount field unchanged.
* When split amounts needs to be adjusted, moneyGuru always adjust them from the 2 **main splits** (see below). Amounts from other splits are never touched.
* The 2 main splits in a transaction are the first split of each side.
* Main splits are displayed in bold.
* You can use drag and drop to re-order splits.
* When one of the main splits is edited, the transaction's Amount value will be adjusted.
* If the transaction is a [Multi-Currency Transaction](currencies.htm), the Amount field cannot be directly set. It can only be edited through splits directly. The read-only amount shown represents a conversion of all amounts of the transaction's splits in your native currency, divided by 2.