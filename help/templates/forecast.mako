<%!
	title = 'Forecasting'
	selected_menu_item = 'Forecasting'
%>
<%inherit file="/base_mg.mako"/>

Some transactions happen in a regular manner, like salaries, utility bills, rent, loan payment, etc.. Some expenses, you can estimate, like groceries, clothing, dining out, etc.. With the scheduling and budgeting features in moneyGuru, you can forecast your financial situation.

Creating a schedule
-----

To create a scheduled transaction, first create a normal transaction which will be the base for the schedule. Then, open the info panel, select a Repeat type, then save. If, for example, you want to create a scheduled bi-weekly salary, first create a normal salary transaction (or select your latest salary transaction), open the info panel, select the "weekly" Repeat type, type "2" in the Every field, then save.

When you create a scheduled transaction, all future occurrences of that schedule for the current date range will be displayed with a little ![](images/clock.png) next to them indicating that they are scheduled.
Editing a schedule
-----

All occurrences of a schedule can be edited like any other transaction. However, there are a few tricks with the &#8679; key you can do to control the schedule.

* **Editing only one occurrence:** If you change a future occurrence like you would with a normal transaction, an exception will be created in the schedule. Only this occurrence will contain the edition you made.
* **Editing all future occurrences:** Sometimes, you want a schedule to be changed from a certain date until the end. To do so, hold &#8679; when you end the edition of the transaction. When you do so, all future occurrences of the schedule will be changed.
* **Skip an occurrence:** Planning an unpaid 3 weeks vacation? Just delete the future occurrences in your salary's schedule just like you would do with a normal transaction.
* **Stop a schedule:** Not all schedules run indefinitely. To stop a schedule at a certain date, just select the occurrence just after the last planned occurrence and delete it while holding &#8679;. All future occurrences will be removed.

As you can see, the concept is rather simple: You can edit scheduled transactions like any other transaction, but by holding &#8679;, the changes you make affect all future occurrences of the schedule.

**When occurrences happen:** Scheduling transactions is all nice, but they have to happen at some point. In moneyGuru, they "happen" when the transaction is reconciled. When you reconcile a scheduled occurrence, it becomes a normal transaction (it loses its ![](images/clock.png) and it can't be used to change future occurrences of the schedule anymore).

Budgeting
-----

When you bring up the info panel of an income or expense account, you have 2 fields you can edit: "Monthly Budget" and "Budget Target". If you set a value for "Monthly Budget" for an expense, the sheets and the charts will include those budgeted amount for future dates. For example, if you set up a 400$ monthly budget for groceries and that you spent 250$ in groceries so far in this month, 150$ in groceries expenses will be spread out evenly for the rest of the month (subsequent months will have the whole 400$ spread out, unless you scheduled future groceries expenses, which would also affect budgeting).

The Budget Target tells moneyGuru where to take money for the budgets from. This way, budgets will affect your assets and liability, and thus, your net worth. You then end up with a really pretty net worth graph.

Forecasting
-----

The scheduling and budgeting features allow for interesting forecasting. First, you can see how sound your budget is by looking at your forecasted net worth for the end of the current year. Also, you can use it to estimate at which point you can afford important financial moves. Planning a 8000$ trip? Look at your balance graph and see at which point you should be able to afford it, then schedule a transaction for it. Planning on buying a house afterwards? Look at which point in the future you'll have enough money for the cash down on the mortgage. Of course, all of this depends on a sound budget...

Forecasting features in moneyGuru are in an embryonate stage. Lots of other nice stuff is coming.
