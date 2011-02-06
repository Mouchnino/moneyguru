Währungen
=========

In moneyGuru können Sie mit verschiedenen Währungen arbeiten, sogar mit unterschiedlichen Währungen pro Transaktion. Jedem Geldbetrag ist eine Währungsinformation zugeordnet, somit können Sie jeden Geldbetrag in jeder beliebigen Währung eingeben. Diese Währungsinformation wird auch immer angezeigt, damit Sie überall wissen, welcher Betrag in welcher Währung eingegeben worden ist.

Zentrales Konzept in moneyGuru ist, dass es zwei unterschiedliche Arten von Währungen gibt. Die **Hauptwährung** wird aus den Systemeinstellungen des Betriebssystems übernommen (Systemeinstellungen --> Sprache & Text --> Formate). Alle anderen vorhandenen Währungen sind **Fremdwährungen**.

Jeder Geldbetrag der Hauptwährung wird ohne Währungsinformation angezeigt, alle anderen Beträge enthalten den dreibuchstabigen ISO Code (USD, GBP, EUR, ...).

Möchten Sie einen Geldbetrag eingeben, so gilt folgende Regel: Verwenden Sie keine Währungsinformation (ISO Code), so gilt der Betrag als gehöre er zur Hauptwährung. Sollten Sie einen Geldbetrag innerhalb eines Kontos eingeben, dem eine andere Währung zugeordnet ist, so gilt ein Betrag ohne Währungsinformation in der dem Konto zugeordneten Währung. Sollte Ihre Hauptwährung der Euro (EUR) sein, so werden Sie innerhalb eines Kontos, das in US-Dollar (USD) geführt wird, vermutlich Geldbeträge in Dollar eingeben wollen. Natürlich können Sie jeden Betrag immer inklusive Währungsinformation eingeben, dabei ist es aber egal, ob der ISO Code dem Geldbetrag vor- oder nachgestellt wird.

Andere Finanzverwaltungsanwendungen führen oftmals eine automatische Währungsumrechnung durch, sofern Sie einen Transfer zwischen Konten unterschiedlicher Währungen durchführen. Dies ist üblicherweise nicht immer sinnvoll: heben Sie im Urlaub vom Geldautomaten beispielsweise 200 USD ab, so ist der von Ihrem EUR-Konto abgebuchte Betrag in den seltensten Fällen mit dem Tageskurs berechnet. Die Tageswechselkurse sind in solchen Fällen eher Schätzwerte. Wie auch immer, in moneyGuru brauchen Sie sich keine Sorgen um automatische Umrechnungen zu machen, denn jede Transaktion behält Ihren Wert in der eingegebenen Währung (im vorigen Beispiel also 200 USD). Möchten Sie die Transaktion mit dem korrekten EUR Betrag korrigieren, so warten Sie auf den Kontoauszug und aktualisieren Sie die Transaktion mit dem richtigen EUR Betrag (in EUR als Währung).

Obwohl moneyGuru Transaktionen immer in der eingegebenen Währung führt (also keine automatische Umrechnung anhand von Wechselkursen vornimmt), werden Wechselkurse jedoch für die Berechnung und Darstellung des Finanzüberblicks in den Ansichten Eigenkapital, Profit & Verlust sowie der Berechnung der Gesamtsummen. Sollten hier Konten mit Fremdwährungen mit einberechnet werden, so sind die Summen mit den Tageskursen in die Hauptwährung umgerechnet. Die Wechselkurse werden bei bestehender Internetverbindung tagesaktuell gehalten und basieren auf den Informationen der "Bank of Canada" beziehungsweise "Yahoo Finance".

Transaktionen mit Teilbeträgen in unterschiedlichen Währungen
-------------------------------------------------------------

Der Großteil der Transaktionen, auch wenn sie in unterschiedlichen Währungen getätigt werden, werden üblicherweise immer nur in einer Währung getätigt. Wenn Sie bei Ebay einen Artikel um 200 USD ersteigern und ihn mit Ihrer Kreditkarte bezahlen, tragen Sie möglicherweise im Voraus bereits eine Transaktion mit besagten 200 USD von Ihrem Kreditkartenkonto auf ein Ausgabekonto ein. Sobald Sie die Kreditkartenabrechnung in Händen halten, werden Sie die Transaktion auf die Hauptwährung umändern, um den korrekten Betrag einzugeben.

In seltenen Fällen gibt es aber auch die Möglichkeit, dass Sie einen Transfer zwischen Aktiva / Passiva Konten durchführen, unter anderem auch mit Konten in einer Fremdwährung. Transferieren Sie beispielsweise 100 EUR auf ein Dollarkonto, das Sie besitzen, so besteht aufgrund der doppelten Buchführung diese Transaktion aus zwei Seiten, wobei eine Seite weiter in EUR, die andere Seite weiterhin in USD geführt werden muss.

Dies stellt natürlich ein Problem für das System der doppelten Buchführung dar, bei der bekanntermassen jede Transaktion ausgeglichen sein muss. Daher gilt folgende Regel: **Eine Transaktion, deren Teilbeträge mehr als eine Währung umfassen, ist immer ausgeglichen**. Im oben angeführten Beispiel bedeutet dies, dass auf einer Seite 100 EUR abgebucht, und auf der anderen Seite 153 Dollar aufgebucht werden.

Um so eine Transaktion zu erstellen, muss der Betrag zweimal eingegeben werden. Im obigen Beispiel würden Sie also eine Transaktion von 100 EUR von Ihrem Girokonto auf das Dollarkonto eingeben. Danach wechseln Sie zum Dollarkonto und editieren die dort vorhandene Transaktion von 100 EUR auf 153 USD. moneyGuru erkennt nun anhand der Währung des Debitkontos die andere Währung und erzeugt automatisch eine Multiwährungs-Transaktion.

Tageswechselkurse sind nie hunderprozentig genau und stellen nur Schätzungen dar, jedoch gibt es noch das Problem, dass Banken und Kreditkartenfirmen bei Überweisungen zwischen Konten unterschiedlicher Währungen meist Kurse die leicht unterhalb des Tageswechselkurses verwenden. Im Dialogfenster für die Transaktionsdetails gibt es Die "Währungssaldo" Schaltfläche. Wenn Sie auf diese klicken, so wird ein neuer Eintrag mit der Differenz des eingegebenen Betrags sowie dem anhand des Wechselkurses berechneten eigentlichen Betrag der Transaktion hinzugefügt. Damit können Sie auch die Wechselgewohnheiten Ihrer Bank beziehungsweise Ihrer Kreditkartenfirma aufzeichnen.

Allgemeine Regeln zu der Verwendung von Währungen
-------------------------------------------------

* Fremdwährungen werden **immer** explizit mit dem Währungscode angezeigt
* Eingegebene Beträge mit einem gültigen Währungscode machen den Betrag **immer** zu einem Betrag in dieser Währung
* Ein Betrag ohne Währungscode ist immer in der Hauptwährung, ausser

    * Beträge, die in der Kontoansicht eines Konto, der eine Fremdwährung zugeordnet ist, eingegeben werden
    * Teiltransaktionen einer Transaktion, die einer Fremdwährung zugeordnet ist

* Eigenkapital sowie Profit & Verlust werden immer in der Hauptwährung berechnet und angezeigt
* Eine Transaktion, die Teiltransaktionen mit unterschiedlichen Währungen beinhaltet, ist immer ausgeglichen

Unterstützte Währungen
----------------------

* [USD] U.S. Dollar
* [EUR] Euro
* [GBP] Pfund Sterling (Großbritannien)
* [CAD] Dollar (Kanada)
* [AUD] Dollar (Australien)
* [JPY] Yen (Japan)
* [INR] Rupie (Indien)
* [NZD] Dollar (Neuseeland)
* [CHF] Schweizer Franken
* [ZAR] Rand (Südafrika)
* [AED] Dirham (VAE)
* [ANG] Florin (Niederländische Antillen)
* [ARS] Argentinischer Peso
* [ATS] Schilling (Österreich)
* [BBD] Dollar (Barbados)
* [BEF] Belgische Franc
* [BHD] Dinar (Bahrain)
* [BRL] Real (Brasilien)
* [BSD] Dollar (Bahamas)
* [CLP] Peso (Chile)
* [CNY] Renminbi Yuan (China)
* [COP] Peso (Kolumbien)
* [CZK] Krone (Tschechische Republik)
* [DEM] Deutsche Mark
* [DKK] Krone (Dänemark)
* [EGP] Pfund (Ägypten)
* [ESP] Peseta (Spanien, Andorra)
* [FIM] Markka (Finnland)
* [FJD] Dollar (Fidschi)
* [FRF] Französischer Franc
* [GHC] Ghana Cedi
* [GHS] Ghana Cedi (neu)
* [GRD] Drachmen (Griechenland)
* [GTQ] Quetzal (Guatemala)
* [HKD] Dollar (Hong Kong)
* [HNL] Lempira (Honduras)
* [HRK] Kuna (Kroatien)
* [HUF] Forint (Ungarn)
* [IDR] Rupiah (Indonesien)
* [IEP] Irisches Pfund
* [ILS] Schekel (Israel)
* [ISK] Krone (Island)
* [ITL] Lira (Italien)
* [JMD] Dollar (Jamaica)
* [KRW] Won (Südkorea)
* [LKR] Rupie (Sri Lanka)
* [LTL] Litas (Litauen)
* [LVL] Latvian lats
* [MAD] Dirham (Marokko)
* [MMK] Kyat (Myanmar, vormals Burma)
* [MXN] Peso (Mexiko)
* [MYR] Ringgit (Malaysia)
* [MZN] Mozambican metical
* [NLG] Gulden (Niederlande)
* [NOK] Krone (Norwegen)
* [PAB] Balboa (Panama)
* [PEN] Nuevo Sol (Peru)
* [PHP] Peso (Philippinen)
* [PKR] Rupie (Pakistan)
* [PLN] Zloty (Polen)
* [PTE] Escudo (Portugal)
* [RON] Neuer Leu (Rumänien)
* [RSD] Dinar (Serbien)
* [RUB] Neuer Rubel (Russland)
* [SEK] Krone (Schweden)
* [SGD] Dollar (Singapur)
* [SIT] Tolar (Slowenien)
* [SKK] Krone (Slowakei)
* [THB] Baht (Thailand)
* [TND] Dinar (Tunesien)
* [TRL] Lira (Türkei)
* [TWD] Dollar (Taiwan)
* [UAH] Hrywnja (Ukraine)
* [VEB] Bolivar (Venezuela)
* [VEF] Bolivar Fuerte (Venezuela)
* [VND] Đồng (Vietnam)
* [XAF] Franc (Zentralafrikanische Wirtschafts- und Währungsunion)
* [XCD] Dollar (Ostkaribische Währungsunion)
* [XPF] Franc (Neukaledonien)
