Často kladené dotazy
====================

.. dotaz: Co je moneyGuru?

    moneyGuru je nástroj na správu a plánování osobních financí. S jeho pomocí můžete vyhodnocovat svoji aktuální finanční situaci a činit informovaná (a tudíž lepší) finanční rozhodnutí.

.. dotaz: V čem je lepší než ostatní aplikace pro správu osobních financí?

    Místo aby moneyGuru podával zprávy, které byste si museli nastavit (nebo si najít tu správnou z přednastavených), máte svá důležitá finanční data (čisté jmění, zisk) neustále aktuální a "před očima". Tak můžete neustále činit informovaná rozhodnutí. moneyGuru má také propracované :doc:`procházení <basics>` a :doc:`editaci <editing>` dokumentu, výbornou podporu :doc:`různých měn <currencies>` a je založený na podvojném účetnictví.

.. dotaz: Jaká jsou omezení zkušební verze moneyGuru?

    Žádná, moneyGuru je `Fairware <http://open.hardcoded.net/about/>`__.

.. dotaz: Jak určím měnu částky?

    Prostě zapište ISO kód měny před nebo za částku, např. "42 eur" nebo "pln 42".

.. dotaz: K čemu jsou ty zelené fajfky v pohledu Účet?

    Ty označují :doc:`spárovanou <reconciliation>` transakci.

.. dotaz: Jak nastavím výchozí zůstatek na účtu?

    Vytvořte transakci Výchozí zůstatek s nejdřívějším možným datem a nepřiřazujte jí přesun.

.. dotaz: Importoval jsem z QIF účet v cizí měně a moneyGuru jí špatně identifikuje. Co s tím?

    Soubory QIF neobsahují informaci o měně. Proto je moneyGuru vždy importuje ve vaší **vlastní** měnu. Opravíte to tak, že před importem přes Detaily účtu změníte měnu, ve které je účet veden. To ale **nezmění** měnu u částek. Tu změníte pomocí hromadných úprav. Přejděte na daný účet, vyberte všechny transakce a zvolte Zobrazit informace (|cmd|\ I). Zobrazí se panel Hromadné úpravy. V políčku měna vyberte měnu importovaného účtu, přesvědčte se, že je u ní zaškrtnuté políčko a stiskněte tlačítko Uložit.

.. dotaz: Některé mé účty jsou v pohledu Čisté jmění a Zisky zašedlé. Proč?

    Zašedlé účty jsou vyloučené.  Vyloučené účty se nezapočítávají do souhrnů. Chcete-li je zahrnout, vyberte takový účet a klepněte na ikonu |basics_account_in|.

.. dotaz: Mám ještě jinou otázku. Co mám dělat?

    There's a `moneyGuru forum`_ which can probably help you. If it's a bug report or feature
    request you have, you should head to `moneyGuru's issue tracker on GitHub`_.

.. _moneyGuru forum: http://forum.hardcoded.net/
.. _moneyGuru's issue tracker on GitHub: https://github.com/hsoft/moneyguru/issues
.. |basics_account_in| image:: image/basics_account_in.png