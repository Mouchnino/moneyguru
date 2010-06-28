<%!
	title = 'Reconciliation'
	selected_menu_item = 'Reconciliation'
%>
<%inherit file="/en/base_mg.mako"/>

The purpose of reconciliation is to stay in sync with your bank statements and make sure you're not missing anything. To do that, look at your bank statement, locate the position of the last unreconciled transaction, and one by one, make sure that the transactions' date and amount are the same in both moneyGuru and in the statement. When they are, reconcile them.

To achieve that, you must go in reconciliation mode. First, select the account you want to reconcile in the Balance Sheet and show it in the Account view. Then, click on the Reconciliation button(or press ${cmd_shift}R). This will toggle reconciliation mode and put checkboxes next to every transaction. When you verified that a transaction matches your statement, check the checkbox next to it to indicate that it's reconciled. You can also select the transaction and press Space. Once you're finished, toggle the reconciliation mode to go back to normal. The boxed check mark will be changed into a green check mark like this: ![](../images/reconciliation_checkmark.png).

When in reconciliation mode. the balance shown in the "Balance" column is the *reconciled* balance rather than the normal balance. The reconciled balance is the balance of all entries that are reconciled or pending reconciliation. Normally, this balance should follow your bank statement's balance.

There is also an additional column (${cmd}J to toggle) you can use in the Account view, the "Reconciliation Date" column. This column is empty when an entry is not reconciled, but when it is, it's supposed to contain the date the entry has on your bank statement. By default, reconciling an entry sets its Reconciliation Date field to the value in the Date column. However, there's sometimes a discrepancy between a transaction's date and the date at which a bank records it. If you want to record that discrepancy, you can manually change the value of that column. Note that if you change the Reconciliation Date of an entry that was not previously reconciled, this entry will automatically become reconciled.
