<%!
	title = 'Importing data into moneyGuru'
	selected_menu_item = 'Import'
%>
<%inherit file="/en/base_mg.mako"/>

moneyGuru support QIF, OFX, QFX and CSV formats for import. To import a file, use the "Import..." item in the "File" menu, then select a file to import. When you do so, the import window will appear, which looks like this:

![](../images/import_window.png)

For each account present in the import file a tab will be added in the import window. This dialog is rather straightforward to use. The leftmost column with a checkbox determines which transactions will be imported. Review the transaction to import, uncheck any transaction you don't want to import, click on import. Only one account (the selected one) is imported at once.

Fixing the dates
-----

moneyGuru automatically determines the date format of any file you import. It looks at all the dates and only chooses a date format that makes sense for all these dates. However, imported files sometimes only contain ambiguous dates (like "01/02/03"), so moneyGuru can't guess a date format with certainty. In these cases, moneyGuru will just pick the first fitting format. What happens when it picks the wrong one? Use the Swap button! For example, if moneyGuru chose dd/mm/yy but your file in fact contained mm/dd/yy, select "Day <--> Month" in the top right box and then click Swap. You can apply the swap to all accounts in the Import window by checking the "Apply to all accounts" box before you do the swap.

Swapping description and payee
-----

In some cases, description and payee fields are swapped. It might be caused by a mistake from the application that created the file, or an ambiguity in the file format, or whatever. It doesn't matter, because you can fix it in the import window. Just select the "Description <--> Payee" in the swap selector, and click "Swap". Problem fixed.

Importing into an existing account
-----

By default, transactions are imported in a new account. However, if you want, you can import transactions in an existing account by changing the target account. When importing OFX files, the target account is automatically selected if appropriate. If you select a target account, the matching table changes slightly and becomes something like this:

![](../images/import_match_table.png)

The reason why the table changes like this is because when you import in an existing account, it is possible that you import transactions that already exist in your account. You must tell moneyGuru which transactions go with which. If you import an OFX file, all of this is done automatically, but you still can change the matching manually if you want.

On the left side of the table (the 3 first columns) are the [unreconciled](reconciliation.htm) transactions from the target account. On the right side are the transactions to be imported. Unmatched transactions have one of their side empty. Matched transaction have both their side filled, and a lock icon in the middle. You can break up matched transactions by clicking on the lock. You can match transactions together by drag & dropping a transaction on another one.

If you import a OFX file for an account that already received an OFX import before, all of this matching happen automatically. This bring up an exception to the rule that only unreconciled transactions are shown in the left side. If a transaction in the imported OFX file matches with a reconciled transaction from the target account, this transaction will be brought up. However, the "import" checkbox will be automatically unchecked (it's normally checked by default). The reason for this is that if it's reconciled, you probably don't want to change it.

CSV Import
-----

Importing CSV files is the same thing as importing another type of file, but before you can get to the main Import window, you have to tell moneyGuru what each CSV column is about.

![](../images/import_csv_options.png)

The problem with CSV is that there is absolutely no standard as to how the file is structured. This window lets you tell moneyGuru what column is what. To use it, look at the data displayed, and when you figured out what one column is about (for example, the date), click on that column's header and select the appropriate transaction field for it. The Date and Amount columns are mandatory.

CSV files also often have header (and even sometimes, footer!) lines. moneyGuru has no clue, beforehand, which lines are what. Therefore, it is you who must uncheck the Import column for each line that does not represent a transaction.

Sometimes, CSV files are so weird that moneyGuru won't be able to correctly detect the delimiter that separates fields in it. If that happens, you'll have all kinds of weird data in your column, with half a value in one column and the other half in another column. In those cases, you can use the **Delimiter** field to manually specify a field delimiter for a CSV file. After you do that, press Rescan to reload the columns using that delimiter.

moneyGuru remembers about columns and header lines between running sessions. If you have more than one type of CSV to regularly import, you can use the Layouts. Each layout store its own column/header configuration.

It's also possible to specify a target account directly in the CSV options window. This achieves the same thing as specifying the target account later, in the Import window, except that if you specify it in the CSV options window, it will be saved in the layout.
