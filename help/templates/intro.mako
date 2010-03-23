<%!
	title = 'Introduction to moneyGuru'
	selected_menu_item = 'introduction'
%>
<%inherit file="/base_mg.mako"/>

moneyGuru is a personal finance management application. With it, you can evaluate your current financial situation so you can make informed (and thus better) financial decisions. Most finance applications have the same goal, but moneyGuru's difference is in the way it achieves it. Rather than having reports which you have to configure (or find out which pre-configured report is the right one), your important financial data (net worth, profit) is constantly up-to-date and "in your face". This allows you to constantly make informed decision rather than doing so periodically.

moneyGuru has a very efficient [navigation](basics.htm) and [editing](edition.htm) system which allows you to painlessly go around your accounts and transactions and modify them. Keyboard shortcuts are neatly designed and efficient. Values are auto-completed when it makes sense. Date edition uses a special widget that lets you edit dates with the least possible number of keystrokes, regardless of your date format.

moneyGuru is loosely based on the [double-entry accounting](http://en.wikipedia.org/wiki/Double-entry_bookkeeping_system) system, where every account -- including income and expenses -- is a first class account, not just a category. It allows for a lot of flexibility in finance management strategies (such as [cash management](cash.htm)).

moneyGuru's support for [currencies](currencies.htm) is way ahead all competitors. Where those who bother with currencies at all do it half-heartedly with poorly thought out designs, currencies are at the core of moneyGuru's design.

<%def name="meta()"><meta name="AppleTitle" content="moneyGuru Help"></meta></%def>