Importing data into moneyGuru
=============================

moneyGuru support QIF, OFX, QFX and CSV formats for import. To import a file, use the "Import..." item in the "File" menu, then select a file to import. When you do so, the import window will appear, which looks like this:

|import_window|

For each account present in the import file a tab will be added in the import window. This dialog is rather straightforward to use. The leftmost column with a checkbox determines which transactions will be imported. Review the transaction to import, uncheck any transaction you don't want to import, click on import. Only one account (the selected one) is imported at once.

Fix broken fields
-----------------

moneyGuru does its best to automatically import the correct data from the files you import. However,
doing it 100% of the time is impossible because sometimes, the value is ambiguous (especially in
the case of date formats). When this happens, moneyGuru will import the value that it thinks is best
and give you the opportunity to fix the manually through the box at the upper-right part of the
import window. This box has a list of 5 fixes you can apply:

* The 3 first fixes are for dates.
* The 4th swaps the Payee and Description fields.
* The last inverts amounts.

It's possible to have an imported file where all dates are ambiguous (like "01/02/03"). moneyGuru
won't be able, in these cases, to determine a correct format. It will pick the one it thinks is
correct, but it might very well be wrong. The first 3 elements will allow you to fix this situation.
Their text will show something like "dd/MM/yy --> MM/dd/yy". The left part is the format that was
used to read the dates and the right part will the format that will be used if you click on "Fix".
It's possible that when you select one of the 3 date-fixing elements, the "Fix" button becomes
disabled. That's because performing this fix would result in one or more dates being incorrect
(for example, a date on the 13th month). moneyGuru won't perform such fixes.

In some cases, description and payee fields are swapped. It might be caused by a mistake from the
application that created the file, or an ambiguity in the file format, or whatever. It doesn't
matter, because you can fix it with the 4th element in the fix list.

Lastly, the last element in the list allow you to invert amounts, that is, convert "42.00" in
"-42.00". You're rarely going to need it, but if you do, you're going to be happy that the option
is there.

Lastly, and this for any fix, enabling the "Apply to all accounts" will apply the fix in all
imported accounts for which the fix is doable.

Importing into an existing account
----------------------------------

By default, transactions are imported in a new account. However, if you want, you can import transactions in an existing account by changing the target account. When importing OFX files, the target account is automatically selected if appropriate. If you select a target account, the matching table changes slightly and becomes something like this:

|import_match_table|

The reason why the table changes like this is because when you import in an existing account, it is possible that you import transactions that already exist in your account. You must tell moneyGuru which transactions go with which. If you import an OFX file, all of this is done automatically, but you still can change the matching manually if you want.

On the left side of the table (the 3 first columns) are the :doc:`unreconciled <reconciliation>` transactions from the target account. On the right side are the transactions to be imported. Unmatched transactions have one of their side empty. Matched transaction have both their side filled, and a lock icon in the middle. You can break up matched transactions by clicking on the lock. You can match transactions together by drag & dropping a transaction on another one.

If you import a OFX file for an account that already received an OFX import before, all of this matching happen automatically. This bring up an exception to the rule that only unreconciled transactions are shown in the left side. If a transaction in the imported OFX file matches with a reconciled transaction from the target account, this transaction will be brought up. However, the "import" checkbox will be automatically unchecked (it's normally checked by default). The reason for this is that if it's reconciled, you probably don't want to change it.

CSV Import
----------

Importing CSV files is the same thing as importing another type of file, but before you can get to the main Import window, you have to tell moneyGuru what each CSV column is about.

|import_csv_options|

The problem with CSV is that there is absolutely no standard as to how the file is structured. This window lets you tell moneyGuru what column is what. To use it, look at the data displayed, and when you figured out what one column is about (for example, the date), click on that column's header and select the appropriate transaction field for it. The Date and Amount columns are mandatory.

CSV files also often have header (and even sometimes, footer!) lines. moneyGuru has no clue, beforehand, which lines are what. Therefore, it is you who must uncheck the Import column for each line that does not represent a transaction.

Sometimes, CSV files are so weird that moneyGuru won't be able to correctly detect the delimiter that separates fields in it. If that happens, you'll have all kinds of weird data in your column, with half a value in one column and the other half in another column. In those cases, you can use the **Delimiter** field to manually specify a field delimiter for a CSV file. After you do that, press Rescan to reload the columns using that delimiter.

moneyGuru remembers about columns and header lines between running sessions. If you have more than one type of CSV to regularly import, you can use the Layouts. Each layout store its own column/header configuration.

It's also possible to specify a target account directly in the CSV options window. This achieves the same thing as specifying the target account later, in the Import window, except that if you specify it in the CSV options window, it will be saved in the layout.

.. |import_window| image:: image/import_window.png
.. |import_match_table| image:: image/import_match_table.png
.. |import_csv_options| image:: image/import_csv_options.png
