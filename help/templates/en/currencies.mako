<%!
	title = 'Currencies'
	selected_menu_item = 'Currencies'
%>
<%inherit file="/en/base_mg.mako"/>

moneyGuru has strong support for multiple currencies. Every amount has a currency information. Any amount you type can be in any currency. A lot of efforts have been made to make sure that you always know what currency any amount is without hurting your eyes and putting explicit currency codes everywhere.

One central concept in moneyGuru is that there are 2 types of currencies. The **native** currency and the **foreign** currencies. The native currency is your system's currency (defined in System Preferences --> International). The foreign currencies are all the others.

The display of these currencies works with a very simple rule: If the amount is in your native currency, it is shown plainly. If it's not, it is shown with the currency's 3 letter ISO code (USD, CAD, EUR, GBP, etc..).

The rules for amount typing are just a little more complex: In almost all cases, typing a number without any currency code means that this amount will be of your native's currency. However, if you are on the Account view with an account that is not of your native's currency, typing an amount without any currency code will create an amount with the **account**'s currency. The reason for this is that even if your native currency is USD, when you are in a EUR account you **very** likely want to type a EUR amount. Of course, in **all cases**, explicitly typing a currency code either in front or after the number makes an amount of that currency.

Some other applications do automatic conversion of amount on transfer between accounts of different currencies. That doesn't make much sense because if you withdraw 200 EUR in an ATM while on a trip, the amount that will be removed from your USD account is pretty much **certain** not to be of the exact exchange rate for that day. Anyway, exchange rate information are estimates and must be treated as such. In moneyGuru, the currencies for an amount just stay as is (200 EUR) until you tell it otherwise (you change the amount to USD after having received your bank statement).

Although moneyGuru doesn't use exchange rate to convert amounts in transactions, it does use them for another purposes: net worth, profit and running balances estimates. Your net worth and profits in moneyGuru are always displayed in your native currency. If you have an account of a foreign currency, you can't have exact values anymore. When this happens, moneyGuru automatically fetches the rates for each transaction's date and use those rates. For the running balance, it's possible that you temporarily have an amount of a foreign currency in one of your asset or liability. Until you reconcile this amount (and change it to the account's currency), the running balance that is shown will be an estimate.

Multiple Currencies Transactions
-----

The vast majority of your transactions, even if you use multiple currencies, will only contain one currency at once. If you buy a 200 EUR widget on Ebay with your USD credit card (which will create a Credit Card --> Widgets transaction for 200 EUR), when you reconcile your Credit Card account, that amount will be changed to USD (the credit card will charge you a USD amount for that 200 EUR).

However, if you make a transfer from an asset or liability to another asset or liability of a different currency, the rules change. If for example you transfer 100 USD from your bank to a EUR bank account you have, then one side of the transaction has to stay in USD, and the other side has to stay in EUR.

This is a tricky problem. Because exchange rates are estimates, there is no way to balance that transaction and, as you know, transaction must always balance. Therefore, an exception to the rule: **A transaction involving more than one currency always balances**. In the example above, we will end up with a transaction that credits 100 USD from one side and debits 65 EUR on the other side.

To create a multiple currencies transaction, just go to the "other side" of the transaction and type the amount in that other currency. You can also use the transaction panel to manually edit the entries. For example, to add that transaction described above, you would first go to Checking, add a transaction for 100 USD and a transfer to "EUR Account". Then you go to "EUR Account" and change the 100 USD amount to 65 EUR. moneyGuru will automatically detect that the "other side" is an asset of a different currency and that the 100 USD on that other side must be preserved thus, creating a multiple currencies transaction.

Even if exchange rates are always estimates, banks and credit card companies have this tendency of always giving you a lower-than-the-current exchange rate for your transactions involving more than one currency. Therefore, even if multiple currencies transactions always balance, you sometimes want to use the exchange rate to be able to balance the transaction so that you can count this difference between the current exchange rate and the rate given to you by the bank as an expense. This is what the **Multi-Currency Balance** button in the Transaction Info panel is for. When you click on it, a new entry will be created in the transaction with the difference between the "two sides" of the transaction when using the exchange rates for the transaction's date.

Currency Rules
-----

* Amounts of foreign currencies are **always** explicitly displayed with their ISO code.
* Explicitly typing the ISO code of a currency for an amount **always** makes this amount an amount of the specified currency.
* Typing a plain amount always results in a native amount, except when:
    * editing an account of a foreign currency.
    * editing splits of a foreign transaction.
* Net worth and profits are calculated in the native currency.
* A transaction involving more than one currency always balances.

Supported Currencies
-----

* [USD] U.S. dollar
* [EUR] European Euro
* [GBP] U.K. pound sterling
* [CAD] Canadian dollar
* [AUD] Australian dollar
* [JPY] Japanese yen
* [INR] Indian rupee
* [NZD] New Zealand dollar
* [CHF] Swiss franc
* [ZAR] South African rand
* [AED] U.A.E. dirham
* [ANG] Neth. Antilles flori
* [ARS] Argentine peso
* [ATS] Austrian schillin
* [BBD] Barbadian dollar
* [BEF] Belgian franc
* [BHD] Bahraini dinar
* [BRL] Brazilian real
* [BSD] Bahamian dollar
* [CLP] Chilean peso
* [CNY] Chinese renminbi
* [COP] Colombian peso
* [CZK] Czech Republic koruna
* [DEM] German deutsche mark
* [DKK] Danish krone
* [EGP] Egyptian pound
* [ESP] Spanish peseta
* [FIM] Finnish mark
* [FJD] Fiji dollar
* [FRF] French franc
* [GHC] Ghanaian
* [GHS] Ghanaian cedi (new)
* [GRD] Greek drach
* [GTQ] Guatemalan quetzal
* [HKD] Hong Kong dollar
* [HNL] Honduran lempira
* [HRK] Croatian kuna
* [HUF] Hungarian forint
* [IDR] Indonesian rupiah
* [IEP] Irish pound
* [ILS] Israeli new shekel
* [ISK] Icelandic krona
* [ITL] Italian lira
* [JMD] Jamaican dollar
* [KRW] South Korean won
* [LKR] Sri Lanka rupee
* [LTL] Lithuanian litas
* [MAD] Moroccan dirham
* [MMK] Myanmar (Burma) kyat
* [MXN] Mexican peso
* [MYR] Malaysian ringgit
* [NLG] Netherlands guild
* [NOK] Norwegian krone
* [PAB] Panamanian balboa
* [PEN] Peruvian new sol
* [PHP] Philippine peso
* [PKR] Pakistan rupee
* [PLN] Polish zloty
* [PTE] Portuguese escudo
* [RON] Romanian new leu
* [RSD] Serbian dinar
* [RUB] Russian rouble
* [SEK] Swedish krona
* [SGD] Singapore dollar
* [SIT] Slovenian tolar
* [SKK] Slovak koruna
* [THB] Thai baht
* [TND] Tunisian dinar
* [TRL] Turkish lira
* [TWD] Taiwanese new dollar
* [UAH] Ukrainian hryvnia
* [VEB] Venezuelan bolivar
* [VEF] Venezuelan bolivar fuerte
* [VND] Vietnamese dong
* [XAF] CFA franc
* [XCD] East Caribbean dollar
* [XPF] CFP franc
