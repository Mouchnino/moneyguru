<%!
	title = 'Reconciliation'
	selected_menu_item = 'Reconciliation'
%>
<%inherit file="/base_mg.mako"/>

If you ever used other finance management applications, reconciliation is probably nothing more to you than a dialog that says "congratulation, your balance matches". In moneyGuru, it's a little different. Reconciliation means that you tell moneyGuru that a transaction has the correct amount at the correct date and results in the correct running balance. Once you told moneyGuru that, **it stays that way**. moneyGuru will not let you do any action that will change the amount or running balance of a reconciled entry without explicitly warning you.

"Why?" you might ask. Changing a reconciled transaction never happens in the real world. In fact, it is very possible that you will never get a reconciliation warning from moneyGuru at all. However, this reconciliation system, hopefully, will make you trust the system. Has it ever happened to you that you avoided OFX imports because you were worried that it would change your old transactions without you noticing? Tweaked income/expense transfers on old, reconciled transactions not being sure exactly if you would end up messing your reconciliation by accident? Trust is what this system is about.

The purpose of reconciliation is to stay in sync with your bank statements and make sure you're not missing anything. To do that, look at your bank statement, locate the position of the last unreconciled transaction, and one by one, make sure that the transactions' date and amount are the same in both moneyGuru and in the statement. When they are, reconcile them.

To achieve that, you must go in reconciliation mode. First, select the account you want to reconcile in the Balance Sheet and show it in the Account view. Then, click on the Reconcile button in the toolbar (or press ${cmd_shift}R). This will toggle reconciliation mode and put checkboxes next to every unreconciled transaction. When you verified that a transaction matches your statement, check the checkbox next to it. You can also select the transaction and press Space. This will put the transaction in "pending" state. Once you're finished, toggle the reconciliation mode again to "commit" pending transaction to a reconciled state. The boxed check mark will be changed into a green check mark like this: ![](images/reconciliation_checkmark.png). Once they're reconciled, they stay reconciled.

If you perform an action that would change the amount or running balance of a reconciled transaction, you will get a warning that looks like this:

![](images/reconciliation_warning.png)

From here, you have 3 choices:

* **Abort action:** The action that was currently being done will be aborted, and reconciliation will not be touched.
* **Continue and unreconcile:** The action that was being done will continue, but all entries affected by this action (either directly or indirectly) will lose reconciliation.
* **Continue, but don't unreconcile:** The action that was being done will continue and no entry will lose reconciliation.

Under normal circumstances, you should either abort the action or continue and unreconcile. However, sometimes it takes a while for a transaction to appear on a statement. Then, a transaction that happened a while ago appears the month after. Some people prefer to use the statement's date for the transaction (in this case, there's no problem), but some people prefer to keep the original transaction date (at the cost of not being in sync with their statements). For the latter case, things get tricky because when you try to reconcile your old transaction, it will trigger that warning. In this case, choose the 3rd option.

One last thing, be aware that unreconciliation can run rather deep. If you change a transaction that has a transfer to another asset or liability that is reconciled, unreconciliation will take place there as well.
