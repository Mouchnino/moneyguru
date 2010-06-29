moneyGuru is loosely based on [double-entry accounting](http://en.wikipedia.org/wiki/Double-entry_bookkeeping_system). The core of the system is the **transaction** which represents a movement of money from some account(s) to some other account(s) at a particular date. A transaction consists in a zero-sum set of 2 or more entries to 2 or more accounts. Any account, whether it's an asset or an income, can send money to any other account. This comes handy when it comes to [cash management](cash.htm). There's not much else to describe for the basics of the system itself. Things get a little more complex when multiple currencies are involved, but the details about that are described on the [currencies page](currencies.htm).

Tabs and views
-----

moneyGuru is based around different views (the main ones are explained below) through which you manage your moneyGuru document. These views are managed through tabs. Tabs behave like any other tab-enabled app. You open a new tab with {cmd}T, you close it with {cmd}W, you can cycle through tabs with {cmd_shift}&#8592;&#8594;. Whenever you open an account with the ![](images/basics_show_account_arrow.png) arrow, a new tab is opened (or if it was already opened, it's selected) for that account.

The date range
-----

The currently selected date range affects the whole application. Everything you see in the views is for the current date range. For example, if August 2008 is selected, everything that you see in all the views is data from 2008/08/01 to 2008/08/31. The range is controlled by this little widget:

![](images/basics_date_range.png)

There are 7 types of date ranges:

1. **Month:** It starts on the first day of a month and ends on the last day of the same month.
1. **Quarter:** It starts on the first day of a quarter (3 months) and ends on the last day of the same quarter.
1. **Year:** It starts on the first day of a year and ends on the last day of the same year.
1. **Year to date:** It starts on the first day of a <i>today's</i> year and ends <i>today</i>. Use this date range if you want moneyGuru to show you your current situation (without any budgeting or scheduled transactions) thrown in the mix.
1. **Running year:** This date range <i>follows</i> today. It displays exactly <i>one year</i>, but instead of displaying full years, it uses the "Ahead months in Running year" preference to determine when the date range ends, and then starts exactly one year before that date.
1. **All Transactions:** This date range starts at the date of the earliest transaction in your document and ends at now + ahead months (see Running Year).
1. **Custom date range:** When you select this date range, moneyGuru will prompt you for a start date and an end date. Afterwards, the date range will be the dates you chose.

For "navigable" date ranges (Month, Quarter, Year), you can use the arrows to select the previous or the next date range (on the keyboard, it's {cmd_opt}[ and {cmd_opt}]). There are also shortcuts to select date range types ({cmd_opt}1-7). You can also press {cmd_opt}T to return to today's date range.

When selecting custom date ranges, you also have the option to have moneyGuru put that date range into one of the 3 available slots. When you do this, a new date range will appear in the menu and will be quickly re-callable.

The thin red line
-----

All information in moneyGuru is displayed according to the currently selected date range. Things get interesting when the date range ends at a future date. If you have scheduled transactions or budget set up, the numbers you will see and the chart you will look at will include them. In the graphs, there is a sharp distinction between the past and the future. The past is displayed in green, and the future is displayed in gray, a thin red line separating both. So when you look at the grey part of graphs, you are looking at stuff that has not happened yet. Your net worth in your balance sheet will count the yet-to-happen scheduled transactions as well as budgets. Sometimes, you just want to know about your current financial situation. This is what the "Year to date" ({cmd_opt}4) date range is for.

Net Worth and Profit & Loss
-----

![](images/basics_net_worth.png)

The Net Worth and Profit &amp; Loss views are where you do account management and get statistics about your financial situation. They both have a similar layout and behave the same way.

**Sheet:** At the top left, there is the "sheet", listing accounts, gives totals account groups. Totals are always given in your native currency. You can also [add, change and remove](edition.htm) accounts from this sheets.

**Show Account:** Next to each account, there is a little ![](images/basics_show_account_arrow.png). You can click on it to show this account in the Account view. You can also select it and press {cmd}&#8594;.

**Account Exclusion:** You can also "exclude" accounts by clicking on the little ![](images/basics_account_out.png) icon, or by pressing space. Excluded accounts are not counted in the sheet's totals or in the charts.

**Pie Chart:** At the right of the sheet of each view are two pie charts showing the weight of every account for each type. If you have account groups, you can collapse one of these groups in the sheet to have the account values grouped in the pie chart. For example, if you have a "Automobile" group with a few related accounts under it, you can collapse the group in the sheet to have "Automobile" as one slice (rather than having one slice for Gas, one slice for Insurance, etc..).

**Graph:** The graph at the bottom of the view shows the progression of the primary view statistic (net worth or profit) over time.

**Columns:** The sheets each have a different set of columns (customizable with {cmd}J).

- **Balance Sheet:**
    - **Account #:** An optional account number reference tied to the account. See the [edition page](edition.htm) for more info.
    - **Start:** The balance of the account at the beginning of the date range. It includes scheduled transactions, but not budgets.
    - **End:** The balance of the account at the end of the date range.
    - **Change:** The difference between Start and End.
    - **Change %:** The difference in percentage between Start and End
    - **Budgeted:** The amount of budget (for which this account is a **target**) left to allocate in this current date range. This means that, if your budgets correctly reflect reality, End + Budgeted should be your actual balance at the end of the date range.
- **Profit & Loss:**
    - **Account #:** Same as in the Balance sheet.
    - **Current:** The cash flow of the account for the current date range.
    - **Last:** The cash flow of the account for the last date range. For example, if in a month range, the Last column shows the cash flow for the month prior to the current one. Year-to-date is a special case and under it, the Last column displays the last year's cash flow.
    - **Change and Change %:** Same as in the balance sheet.
    - **Budgeted:** The amount of budget assigned to this account left to allocate in this current date range. This means that, if your budgets correctly reflect reality, Current + Budgeted should be your actual cash flow at the end of the date range.

Transactions
-----

![](images/basics_transactions.png)

In the Transactions view, all transactions of the document for the current date range are listed. From there, you can [add, change and remove](edition.htm) transactions. This view is the most efficient view for adding a batch of transactions (if you have a pile of invoices and receipts to add, for example). **Amount** contains the value that is transferred by the transaction. **From** and **To** contain the name of the accounts affected by the transaction (if it's a split transaction, names are comma separated). What these 3 columns mean is "This transaction transfers **Amount** from **From** and sent it to **To**". For example, if **From** is "Checking" and **To** is "Groceries", money is taken out of Checking and put in "Groceries". For an income **From** would be "Salary" and **To** would be "Checking".

Above the transactions list, there is a **filter bar** allowing you to see only certain types of transactions.

* **Income:** Show only transactions affecting at least one income account.
* **Expense:** Show only transactions affecting at least one expense account.
* **Transfer:** Show only transactions affecting at least two asset or liability accounts.
* **Unassigned:** Show only transactions having at least one unassigned entry.
* **Reconciled:** Show only transactions having at least one reconciled entry.
* **Not Reconciled:** Show only transactions having no reconciled entry.

**From** and **To** cells have a little ![](images/basics_show_account_arrow.png) at their right. Similarly to the Net Worth and Profit views, you can click on it to show the account displayed in the cell (if, for transactions having more than 2 splits, there's more than one account in the cell, the first account is shown).

Account
-----

![](images/basics_account.png)

This view displays transactions *from the perspective of a specific account*. You can open an Account view by clicking on the ![](images/basics_show_account_arrow.png) in other views. It lists transactions similarly to the Transactions view, but it only lists transactions that affect the shown account. Instead of a **From** and a **To** column, there is only a **Transfer** column (the *other side(s)* of the transaction). However, the **Amount** column is split into an **Increase** and a **Decrease** column. For example, if I have Checking shown and the **Transfer** is "Groceries" and the **Decrease** is "42", it means that 42$ are taken from Checking and sent to Groceries. If the shown account is an asset or liability, there is also a **Balance** column, which shows the running balance of the account. The graph below shows the balance of the account for each day of the date range. If the shown account is an income or an expense, a bar chart similar to the Profit & Loss chart will be shown.

The Account view also has a filter bar, which behaves similarly to the one in the Transactions view, but with slight differences.

* **Increase:** Show only entries that have their amount on the "Increase" side.
* **Decrease:** Show only entries that have their amount on the "Decrease" side.
* **Transfer:** Show only entries that are part of a transaction affecting at least two asset or liability accounts.
* **Unassigned:** Show only unassigned entries.
* **Reconciled:** Show only reconciled entries.
* **Not Reconciled:** Show only un-reconciled entries.

The *Reconciliation* button in the filter bar (only enabled for assets/liabilities) lets you toggle [reconciliation](reconciliation.htm) mode on and off.

**Transfer** cells have a little ![](images/basics_show_account_arrow.png) at their right. Similarly to the other views, you can click on it to show the account displayed in the cell. Unlike arrows from the Transaction view, this only *cycles through* the transaction's split. Therefore, even when a transaction has more than 2 splits, continually clicking on that arrow will show all affected accounts, not just the first 2.

Filtering
-----

The filter field in the toolbar allows you to see all transactions that match the stuff you type in it. To use it, type something and press return. Only transactions that have a description, payee, check #, account or amount matching with what you typed will be shown. If you want to see transactions from specific accounts or groups, type "account: account1,account2" or "group: group1,group2" in the filter box. This is very handy for [mass editing](edition.htm).

View Options
-----

![](images/basics_view_options.png)

moneyGuru has a View options panel allowing you to hide some elements (such as charts). You can toggle its visibility with {cmd}J.

What You See Is What You Print (Kinda)
-----

In moneyGuru, you can print whatever is currently shown in any of the four views. You want to report a transaction listing for last year? Just set the current date range to last year, go to the Transactions view, and press {cmd}P. moneyGuru automatically sizes the columns according to their content (columns with longer data are larger), trying to fit the most data in the page.