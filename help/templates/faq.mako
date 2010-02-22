<%!
	title = 'moneyGuru F.A.Q.'
	selected_menu_item = 'F.A.Q.'
%>
<%inherit file="/base_mg.mako"/>

<%text filter="md">
### What is moneyGuru?

moneyGuru is a personal finance management and planning tool. With it, you can evaluate your current financial situation so you can make informed (and thus better) financial decisions.

### How much does it cost?

The target price for moneyGuru is 49.95. You can buy moneyGuru at the [Hardcoded Software purchase page.](http://www.hardcoded.net/purchase.htm)

### What makes it better than other finance management applications?

Rather than having reports which you have to configure (or find out which pre-configured report is the right one), your important financial data (net worth, profit) is constantly up-to-date and "in your face". This allows you to constantly make informed decision rather than doing so periodically. moneyGuru also has a very efficient [navigation](basics.htm) and [edition](edition.htm) system, a strong support for [currencies](currencies.htm) and a system based on double-entry bookkeeping.

### What are the demo limitations of moneyGuru?

In demo mode, you cannot save a document that has more than 100 transactions.

### How to I specify the currency of an amount?

Just write down the currency ISO code in front of it or after it, like "42 eur" or "pln 42".

### What are those green check marks in the Account view?

They indicate that the transaction is [reconciled](reconciliation.htm).

### How do I set the starting balance of an account?

Create a Starting Balance transaction at the earliest date possible and leave the transfer unassigned.

### I imported an account with a foreign currency from a QIF and the currency is wrong in moneyGuru. What do I do?

QIF files don't contain currency information. Therefore, moneyGuru always import such account as your **native** currency. To fix this, first change the currency of the account through the Account Details. However, this will **not** touch your amounts' currency. To change these, you have to perform a mass edition. Go into your account and select all transactions (you will have to do that in more than one shot if your transactions span on more than one year) and Show Info (&#8984;I). This will bring the Mass Editing panel. In the currency field, select the currency of the account you imported, make sure the little checkbox is checked, and press Save.

### I have another question. What can I do?

You can always send an e-mail to support@hardcoded.net, but the best way to ask a question is to go on [Hardcoded Software's Get Satisfaction site](http://getsatisfaction.com/hardcodedsoftware). Who knows, your question might already have been answered there!

</%text>