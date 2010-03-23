<%!
	title = 'Forecasting'
	selected_menu_item = 'Forecasting'
%>
<%inherit file="/base_mg.mako"/>

Some transactions happen in a regular manner, like salaries, utility bills, rent, loan payment, etc.. Some expenses, you can estimate, like groceries, clothing, dining out, etc.. With the scheduling and budgeting features in moneyGuru, you can forecast your financial situation.

Creating a schedule
-----

To create a scheduled transaction, go the the Schedules view and click on the New Item button. A Schedule Info panel will pop up. This panel is similar to the Transaction Info panel, but has a few extra fields: Repeat Type, Repeat Every and Stop Date. The Repeat type field determines what kind of interval you want (daily, weekly, etc..). The Repeat Every field is to tell how many of that interval type you want between each occurrences. For example, if you want a bi-weekly schedule, you would set the Repeat Type to Weekly, and the Repeat Every to 2.

If you already have a "model transaction" from which you want a schedule to be created, there's a shortcut for this in the menu called Make Schedule From Selected. This will create a new schedule and copy all info from the selected transaction to populate it.

When you create a scheduled transaction, all future occurrences of that schedule for the current date range will be displayed with a little ![](images/clock.png) next to them indicating that they are scheduled.

Editing a schedule
-----

In addition to being able to edit your schedules through the Schedules view, you can also edit *any occurrence of it* in the Transactions or Account view! These occurrences can be edited like any other transaction, but there are a few tricks with the Shift key you can do to control the schedule.

* **Editing only one occurrence:** If you change an occurrence like you would with a normal transaction, an exception will be created in the schedule. Only this occurrence will contain the edition you made.
* **Editing all future occurrences:** Sometimes, you want a schedule to be changed from a certain date until the end. To do so, hold Shift when you end the edition of the transaction. When you do so, all future occurrences of the schedule will be changed.
* **Skip an occurrence:** Planning an unpaid 3 weeks vacation? Just delete the future occurrences in your salary's schedule just like you would do with a normal transaction.
* **Stop a schedule:** Not all schedules run indefinitely. To stop a schedule at a certain date, just select the occurrence just after the last planned occurrence and delete it while holding Shift. All future occurrences will be removed.

As you can see, the concept is rather simple: You can edit scheduled transactions like any other transaction, but by holding Shift, the changes you make affect all future occurrences of the schedule.

**When occurrences happen:** Scheduling transactions is all nice, but they have to happen at some point. In moneyGuru, they "happen" when the transaction is reconciled. When you reconcile a scheduled occurrence, it becomes a normal transaction (it loses its ![](images/clock.png) and it can't be used to change future occurrences of the schedule anymore).

Budgeting
-----

Budgets are similar to schedules in the way they behave. They also create transactions at regular intervals, but instead of creating occurrences with fixed amounts, they create occurrences with **floating** amounts. For example, if you create a 200$ monthly budget for the expense account *Clothes*, it will, like the schedules, create regular occurrences of 200$ every month. However, if you create a transaction that sends 50$ to the *Clothes* account, the budget occurrence for that month will become 150$.

A budget can be created from the Budgets view. The Repeat fields work exactly like they do for the schedules. The Account field is the income or expense account for which the budget is (Clothes, Salary, etc..). The Target field, which is optional, lets you indicate an asset or liability to be used for the other side of the transaction. When you define one, the "future" area of the balance graph in that account will correctly reflect change in its balance that will occur.

It's important to remember that setting a Target account **does not** limit your budget to that target account. For example, if you create a 200$ budget for *Clothes*, with a target to your *Checking* account, buying 50$ worth of clothes with your *Credit Card* account will still correctly affect your budget occurrence for that month and make it go down to 150$.

Forecasting
-----

The scheduling and budgeting features allow for interesting forecasting. First, you can see how sound your budget is by looking at your forecasted net worth for the end of the current year. Also, you can use it to estimate at which point you can afford important financial moves. Planning a 8000$ trip? Look at your balance graph and see at which point you should be able to afford it, then schedule a transaction for it. Planning on buying a house afterwards? Look at which point in the future you'll have enough money for the cash down on the mortgage. Of course, all of this depends on a sound budget...

Forecasting features in moneyGuru are in an embryonate stage. Lots of other nice stuff is coming.
