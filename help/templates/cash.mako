<%!
	title = 'Cash Management'
	selected_menu_item = 'cash'
%>
<%inherit file="/base_mg.mako"/>

Managing cash is a tricky issue in all personal finance applications. The money you have in your wallet is technically an asset. So if you want to go by the book, you would create an account for each currency you have in your wallet. Every time you purchase something with cash, you add a transaction from your cash account to an expense account. However, you certainly don't want to start adding "chocolate bar for .99$" transactions. You don't want to ignore all cash transactions you make either, right? So what you will inevitably have to do is to periodically count the money in your wallet and make an adjustment entry to an expense account like "Undefined cash expenses".

Various finance management application have various solutions for this. Some of them have a hidden and special cash account with which you're not too sure what happens. Most of them have nothing. moneyGuru has the double-entry accounting system. Because every accounts, including income and expenses, are full fledged accounts, you can make transactions going from one expense to another expense. You're beginning to see where it leads...

The Cash expense account
-----

The proposed solution (because if you want, you can totally manage cash as an asset) is to create a "Cash" expense account. When you withdraw money, send it to that expense account. When you purchase something with cash, take it from that account. The leftover will be expenses you had paid in cash for which you never created a transaction (or pennies you lost in the couch).
