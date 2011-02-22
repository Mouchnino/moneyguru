Forecasting
===========

Some transactions happen in a regular manner, like salaries, utility bills, rent, loan payment, etc.. These are fit for **schedules**. Some expenses, you can estimate, like groceries, clothing, dining out, etc.. These are fit for **budgets**. With the scheduling and budgeting features in moneyGuru, you can forecast your financial situation.

How it works
------------

Both schedules and budgets work with a system of "occurrences". When you create a schedule or budget (in the Schedules and Budgets views), you create a "master" transaction. From this master transaction, occurrences will be created at regular intervals (which you define in your master transaction) and will be shown in the Transactions and Account views.

Schedule occurrences can be directly edited from the Transactions and Account views. When you modify such an occurrence, moneyGuru asks you for the scope of your modification. You can either modify just one occurrence (if, for example, a loan payment was exceptionally higher once), or you can choose to give a global scope to your modification, that is, affecting all future occurrences (if, for example, your rent was raised).

When you modify a master schedule, these changes affect all occurrences, *except* for occurrences you manually edited.

Budget occurrences are a little different. They can't be edited, but their amount is affected by other transactions. All transactions affecting a budget's target income/expense account will reduce the amount of the occurrence covering the date of these transactions. For example, if you have a monthly "clothes" budget of 100$, creating a transaction sending 20$ to "clothes" in July will make the "clothes" occurrence of July 31st to be 80$ instead of 100$.

Another specificity of budget occurrences is that they're exclusively *in the future*. As soon as their date is reached, they disappear.

Creating a schedule
-------------------

To create a scheduled transaction, go the the Schedules view and click on the New Item button. A Schedule Info panel will pop up. This panel is similar to the Transaction Info panel, but has a few extra fields: Repeat Type, Repeat Every and Stop Date. The Repeat type field determines what kind of interval you want (daily, weekly, etc..). The Repeat Every field is to tell how many of that interval type you want between each occurrences. For example, if you want a bi-weekly schedule, you would set the Repeat Type to Weekly, and the Repeat Every to 2.

If you already have a "model transaction" from which you want a schedule to be created, there's a shortcut for this in the menu called Make Schedule From Selected. This will create a new schedule and copy all info from the selected transaction to populate it.

When you create a scheduled transaction, all future occurrences of that schedule for the current date range will be displayed with a little |clock| next to them indicating that they are scheduled.

Editing a schedule
------------------

In addition to being able to edit your schedules through the Schedules view, you can also edit *any occurrence of it* in the Transactions or Account view! These occurrences can be edited like any other transaction, but there are a few tricks with the Shift key you can do to control the schedule.

* **Editing only one occurrence:** If you change an occurrence like you would with a normal transaction, an exception will be created in the schedule. Only this occurrence will contain the edition you made.
* **Editing all future occurrences:** Sometimes, you want a schedule to be changed from a certain date until the end. To do so, hold Shift when you end the edition of the transaction. When you do so, all future occurrences of the schedule will be changed.
* **Skip an occurrence:** Planning an unpaid 3 weeks vacation? Just delete the future occurrences in your salary's schedule just like you would do with a normal transaction.
* **Stop a schedule:** Not all schedules run indefinitely. To stop a schedule at a certain date, just select the occurrence just after the last planned occurrence and delete it while holding Shift. All future occurrences will be removed.

As you can see, the concept is rather simple: You can edit scheduled transactions like any other transaction, but by holding Shift, the changes you make affect all future occurrences of the schedule.

**When occurrences happen:** Scheduling transactions is all nice, but they have to happen at some point. In moneyGuru, they "happen" when the transaction is reconciled. When you reconcile a scheduled occurrence, it becomes a normal transaction (it loses its |clock| and it can't be used to change future occurrences of the schedule anymore).

Budgeting
---------

A budget can be created from the Budgets view. The Repeat fields work exactly like they do for the schedules. The Account field is the income or expense account for which the budget is (Clothes, Salary, etc..). The Target field, which is optional, lets you indicate an asset or liability to be used for the other side of the transactions. When you define one, the "future" area of the balance graph in that account will correctly reflect change in its balance that will occur.

It's important to remember that setting a Target account **does not** limit your budget to that target account. For example, if you create a 200$ budget for *Clothes*, with a target to your *Checking* account, buying 50$ worth of clothes with your *Credit Card* account will still correctly affect your budget occurrence for that month and make it go down to 150$.

Normally, the best account to use as budget target is your main checking account since it's where the money is coming from and going to in the end. The purpose of the budget target is to let budgets affect your future balances, so if you target, for example, your credit card account, unless you have a scheduled transaction that regularly pays off the card, your future balance for that credit card will simply grow up indefinitely.

Cashculator Integration
-----------------------

**This feature requires Cashculator v1.2.2 or later.**

The budgeting and scheduling features in moneyGuru are good if you already know what kind of budgets you want to stick to. However, moneyGuru doesn't let you play around with hypothetical budgets in order to design the budget you're going to adopt. There's a nice app from another developer that specializes in that: `Cashculator <http://www.apparentsoft.com/cashculator>`__.

moneyGuru integrates with Cashculator to make it easy for you to export "Actual" (that's what they call it) data to Cashculator, design your budgets, and then add those budgets back to moneyGuru. To use this integration feature, follow these steps:

1. Download Cashculator, run it once (moneyGuru needs Cashculator's skeleton of its database) and close it.
2. Open your moneyGuru document, open a new tab and click on the "Cashculator" button.
3. The tab will show a list of your income and expense accounts. Through this list, you have to choose which of your accounts are Recurring and which and Non-Recurring (it's an important distinction in Cashculator).
4. Click on "Export Accounts". This will export all your income and expense accounts as well as their cash flow for the last 4 months. Don't worry about your regular Cashculator data. moneyGuru makes its own copy of Cashculator's database and exports its data there.
5. Make sure that Cashculator is closed, then click on "Launch Cashculator" which will launch Cashculator. You need to use this button to launch it because it tells Cashculator to use moneyGuru's database instead of its own.
6. In Cashculator, there's going to be a scenario called "moneyGuru" which contains all your accounts as well as their "Actual" data for the last 4 months. Use this data to design yourself a budget (please refer to Cashculator's documentation for that)
7. Once you're done, you can create budgets and schedules according to your design in moneyGuru. You'll have to do it manually, but that's a temporary limitation of the feature (see below).
8. Cashculator will be reverted to normal mode (its regular database) when you quit moneyGuru.

**For now, the Cashculator integration only works one way (export).** The way Cashculator works is very different from the way moneyGuru works. Exporting data isn't so complicated, but when comes the time to import back budgets in moneyGuru, things get a little trickier. There're lots of ways you can fill "Plan" cells out in Cashculator and there's no obvious ways to automatically convert that into budgets and schedules.