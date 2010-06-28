<%!
	title = 'Forecasting'
	selected_menu_item = 'Forecasting'
%>
<%inherit file="/en/base_mg.mako"/>

Some transactions happen in a regular manner, like salaries, utility bills, rent, loan payment, etc.. These are fit for **schedules**. Some expenses, you can estimate, like groceries, clothing, dining out, etc.. These are fit for **budgets**. With the scheduling and budgeting features in moneyGuru, you can forecast your financial situation.

How it works
-----

Both schedules and budgets work with a system of "occurrences". When you create a schedule or budget (in the Schedules and Budgets views), you create a "master" transaction. From this master transaction, occurrences will be created at regular intervals (which you define in your master transaction) and will be shown in the Transactions and Account views.

Schedule occurrences can be directly edited from the Transactions and Account views. When you modify such an occurrence, moneyGuru asks you for the scope of your modification. You can either modify just one occurrence (if, for example, a loan payment was exceptionally higher once), or you can choose to give a global scope to your modification, that is, affecting all future occurrences (if, for example, your rent was raised).

When you modify a master schedule, these changes affect all occurrences, *except* for occurrences you manually edited.

Budget occurrences are a little different. They can't be edited, but their amount is affected by other transactions. All transactions affecting a budget's target income/expense account will reduce the amount of the occurrence covering the date of these transactions. For example, if you have a monthly "clothes" budget of 100$, creating a transaction sending 20$ to "clothes" in July will make the "clothes" occurrence of July 31st to be 80$ instead of 100$.

Another specificity of budget occurrences is that they're exclusively *in the future*. As soon as their date is reached, they disappear.

Creating a schedule
-----

To create a scheduled transaction, go the the Schedules view and click on the New Item button. A Schedule Info panel will pop up. This panel is similar to the Transaction Info panel, but has a few extra fields: Repeat Type, Repeat Every and Stop Date. The Repeat type field determines what kind of interval you want (daily, weekly, etc..). The Repeat Every field is to tell how many of that interval type you want between each occurrences. For example, if you want a bi-weekly schedule, you would set the Repeat Type to Weekly, and the Repeat Every to 2.

If you already have a "model transaction" from which you want a schedule to be created, there's a shortcut for this in the menu called Make Schedule From Selected. This will create a new schedule and copy all info from the selected transaction to populate it.

When you create a scheduled transaction, all future occurrences of that schedule for the current date range will be displayed with a little ![](../images/clock.png) next to them indicating that they are scheduled.

Editing a schedule
-----

In addition to being able to edit your schedules through the Schedules view, you can also edit *any occurrence of it* in the Transactions or Account view! These occurrences can be edited like any other transaction, but there are a few tricks with the Shift key you can do to control the schedule.

* **Editing only one occurrence:** If you change an occurrence like you would with a normal transaction, an exception will be created in the schedule. Only this occurrence will contain the edition you made.
* **Editing all future occurrences:** Sometimes, you want a schedule to be changed from a certain date until the end. To do so, hold Shift when you end the edition of the transaction. When you do so, all future occurrences of the schedule will be changed.
* **Skip an occurrence:** Planning an unpaid 3 weeks vacation? Just delete the future occurrences in your salary's schedule just like you would do with a normal transaction.
* **Stop a schedule:** Not all schedules run indefinitely. To stop a schedule at a certain date, just select the occurrence just after the last planned occurrence and delete it while holding Shift. All future occurrences will be removed.

As you can see, the concept is rather simple: You can edit scheduled transactions like any other transaction, but by holding Shift, the changes you make affect all future occurrences of the schedule.

**When occurrences happen:** Scheduling transactions is all nice, but they have to happen at some point. In moneyGuru, they "happen" when the transaction is reconciled. When you reconcile a scheduled occurrence, it becomes a normal transaction (it loses its ![](../images/clock.png) and it can't be used to change future occurrences of the schedule anymore).

Budgeting
-----

A budget can be created from the Budgets view. The Repeat fields work exactly like they do for the schedules. The Account field is the income or expense account for which the budget is (Clothes, Salary, etc..). The Target field, which is optional, lets you indicate an asset or liability to be used for the other side of the transactions. When you define one, the "future" area of the balance graph in that account will correctly reflect change in its balance that will occur.

It's important to remember that setting a Target account **does not** limit your budget to that target account. For example, if you create a 200$ budget for *Clothes*, with a target to your *Checking* account, buying 50$ worth of clothes with your *Credit Card* account will still correctly affect your budget occurrence for that month and make it go down to 150$.

Normally, the best account to use as budget target is your main checking account since it's where the money is coming from and going to in the end. The purpose of the budget target is to let budgets affect your future balances, so if you target, for example, your credit card account, unless you hace a scheduled transaction that regularly pays off the card, your future balance for that credit card will simply grow up indefinitely.

Forecasting
-----

The scheduling and budgeting features allow for interesting forecasting. First, you can see how sound your budget is by looking at your forecasted net worth for the end of the current year. Also, you can use it to estimate at which point you can afford important financial moves. Planning a 8000$ trip? Look at your balance graph and see at which point you should be able to afford it, then schedule a transaction for it. Planning on buying a house afterwards? Look at which point in the future you'll have enough money for the cash down on the mortgage. Of course, all of this depends on a sound budget...

Forecasting features in moneyGuru are in an embryonate stage. Lots of other nice stuff is coming.
