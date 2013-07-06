Frequently Asked Questions
==========================

.. topic:: What is moneyGuru?

    moneyGuru is a personal finance management and planning tool. With it, you can evaluate your current financial situation so you can make informed (and thus better) financial decisions.

.. topic:: What makes it better than other finance management applications?

    Rather than having reports which you have to configure (or find out which pre-configured report is the right one), your important financial data (net worth, profit) is constantly up-to-date and "in your face". This allows you to constantly make informed decision rather than doing so periodically. moneyGuru also has a very efficient :doc:`navigation <basics>` and :doc:`editing <editing>` system, a strong support for :doc:`currencies <currencies>` and a system based on double-entry bookkeeping.

.. topic:: How to I specify the currency of an amount?

    Just write down the currency ISO code in front of it or after it, like "42 eur" or "pln 42".

.. topic:: What are those green check marks in the Account view?

    They indicate that the transaction is :doc:`reconciled <reconciliation>`.

.. topic:: How do I set the starting balance of an account?

    Create a Starting Balance transaction at the earliest date possible and leave the transfer unassigned.

.. topic:: I imported an account with a foreign currency from a QIF and the currency is wrong in moneyGuru. What do I do?

    QIF files don't contain currency information. Therefore, moneyGuru always import such account as your **native** currency. To fix this, first change the currency of the account through the Account Details. However, this will **not** touch your amounts' currency. To change these, you have to perform a mass edition. Go into your account and select all transactions and Show Info (|cmd|\ I). This will bring the Mass Editing panel. In the currency field, select the currency of the account you imported, make sure the little checkbox is checked, and press Save.

.. topic:: Some of my accounts are grayed out in Net Worth and Profit views, why?

    When accounts are grayed out, it means that they're excluded. Excluded accounts are not counted in totals. To include accounts back, select it and click on the little |basics_account_in| icon.

.. topic:: I have another question. What can I do?
    
    There's a `moneyGuru forum`_ which can probably help you. If it's a bug report or feature
    request you have, you should head to `moneyGuru's issue tracker on GitHub`_.

.. _moneyGuru forum: http://forum.hardcoded.net/
.. _moneyGuru's issue tracker on GitHub: https://github.com/hsoft/moneyguru/issues
.. |basics_account_in| image:: image/basics_account_in.png