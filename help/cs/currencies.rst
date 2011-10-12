Měny
====

moneyGuru má výbornou podporu pro používání různých měn. Každá částka nese informaci o měně. Můžete zapsat libovolnou částku v libovolné měně. Tvůrci vynaložili mnoho úsilí, abyste vždy přesně věděli jaká částka je v jaké měně, aniž byste si museli namáhat zrak nebo všude cpát zkratky měny.

Hlavní myšlenkou moneyGuru je existence 2 druhů měny. **Vlastní** měna a **cizí** měna. Vlastní měna je ta, kterou používá váš operační systém (definuje se v System Preferences --> International). Vše ostatní jsou cizí měny.

Zobrazení měn se řídí prostým pravidlem: Je-li částka ve vlastní měně, zobrazí se bez dalšího popisu. Pokud je suma v cizí měně, zobrazí se třípísmenným kódem ISO (USD, CAD, EUR, GBP atd.).

Pravidla pro zápis částky jsou trošku složitější: Téměř vždy znamená zápis čísla bez kódu měny sumu ve vlastní měně. Pokud jste ale v pohledu Účet na účtu, který není veden ve vlastní měně, bude znamenat zápis bez kódu měny částku v měně, ve které je účet veden. Důvodem je, že i kdyby byl vaší vlastní měnou dolar, pokud pracujete s např. s účtem v eurech, je **velmi** pravděpodobné, že chcete zapsat částku v eurech. Samozřejmě **vždy** když explicitně uvedete kód měny před nebo za číslem, představuje zápis částku v dané měně.

Některé aplikace automaticky převádějí částky do jiné měny při přesunu mezi účty s rozdílnými měnami. To není moc smysluplné, protože když na výletě vyberete z bankomatu 200 EUR, můžete si být **jisti**, že se z vašeho CZK účtu nestrhne částka přesně odpovídající směnnému kurzu toho dne. Směnné kurzy jsou odhady a tak se s nimi musí i pracovat. moneyGuru nemění informaci o použité měně (200 EUR), dokud sami neřeknete opak (tím, že změníte částku na CZK po obdržení výpisu z banky).

I když moneyGuru nepoužívá směnné kurzy pro převody částek v transakci, používá je k jiným účelům: čisté jmění, zisk a odhady aktuálních zůstatků. Vaše čisté jmění a zisky zobrazuje moneyGuru vždy ve vaší vlastní měně. Pokud máte účet v zahraniční měně, nemůžete nikdy získat přesné částky. V takovém případě moneyGuru automaticky stahuje kurzovní lístky pro každé datum transakce a používá je. U aktuálního zůstatku je možné, že u majetku nebo závazku bude nějaká částka dočasně v cizí měně. Dokud tuto částku nespárujete (a nezměníte ji na měnu účtu), bude zobrazený aktuální zůstatek odhadem.

Transakce ve více měnách
------------------------

Většina vašich transakcí, i když používáte více měn, bude obsahovat pouze jednu měnu. Když si na eBayi koupíte za 200 EUR nějakou hračku a zaplatíte ji svojí kreditní kartou vedenou v CZK (čímž vytvoříte transakci 200 EUR z účtu Kreditní karta na účet Hobby), pak se při párování částek na účtu Kreditní karta změní tato suma na CZK (z kreditní karty se v CZK odečte ekvivalent 200 EUR).

Rozdíl nastává, pokud částku přesunete z majetkového účtu nebo závazky na jiný účet jmění nebo závazků vedený v jiné měně. Pokud například přesunete 100 USD ze svého účtu na jiný účet vedený v Eurech, pak jedna strana transakce musí zůstat v USD a druhá musí zůstat jako EUR.

To je docela složitý oříšek. Protože jsou kurzy pouze odhady, neexistuje způsob jak vyrovnat takovou transakci. Ale transakce musí být vždy vyrovnané, že. Proto tu je výjimka potvrzující pravidlo: **Transakce s více než jednou měnou je vždy vyrovnaná**. Výše uvedený příklad se zapíše jako transakce vkladem 100 USD na jedné straně a výběrem 65 EUR na straně druhé.

Transakci s více měnami vytvoříte tak, že na "druhé straně" transakce zapíšete částku v té druhé měně. Také můžete ručně editovat položky v panelu transakcí. Například transakci popsanou výše zadáte následovně: nejprve přejděte na účet Běžný účet a zadejte transakci na 100 USD jako přesun na "Účet EUR". Pak přejděte na "Účet EUR" a změňte 100 USD na částku 65 EUR. moneyGuru automaticky zjistí, že "druhou stranou" je majetkový účet vedený v jiné měně a že oněch 100 USD na první straně je třeba zachovat, a vytvoří transakci s více měnami.

I když jsou kurzy vždy odhadem, banky a společnosti vydávající kreditní karty mají tendenci vám poskytovat nižší než aktuální kurz pro vaše transakce zahrnující více než jednu měnu. Proto i když jsou transakce s více měnami vždy vyrovnané, můžete někdy chtít použít směnný kurz pro vyrovnání transakce, abyste mohli započítat tento rozdíl mezi aktuálním kurzem a kurzem vaší banky jako výdaj. K tomu slouží tlačítko **Vyrovnání u více měn** v panelu Informace o transakci. Když na něj klepnete, vytvoří se u transakce nový záznam, kam zaznamenáte rozdíl mezi "oběma stranami" transakce při použití směnného kurzu ze dne transakce.

Pravidla pro měny
-----------------

* Částky v cizích měnách jsou **vždy** explicitně zobrazeny s odpovídajícím ISO kódem měny.
* Explicitní zápis ISO kódu měny u částky **vždy** znamená, že tato částka je částkou v určené měně.
* Zápis částky bez kódu měny znamená částku ve vlastní měně s výjimkou:

    * úprav účtu vedeného v cizí měně.
    * úprav dělených transakcí v cizí měně.

* Čisté jmění a zisky se počítají ve vlastní měně.
* Transakce, které obsahují více než jednu měnu jsou vždy vyrovnané.

Podporované měny
--------------------

* [USD] Americký dolar
* [EUR] Euro
* [GBP] Britská libra
* [CAD] Kanadský dolar
* [AUD] Australský dolar
* [JPY] Yen
* [INR] Indická rupie
* [NZD] Novozélandský dolar
* [CHF] Švýcarský frank
* [ZAR] Jihoafrický rand
* [AED] Dirham (SAE) 
* [ANG] Flori (Nizozemské Antily) 
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
* [CZK] Česká koruna
* [DEM] Německá marka
* [DKK] Dánská koruna
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
* [LVL] Latvian lats
* [MAD] Moroccan dirham
* [MMK] Myanmar (Burma) kyat
* [MXN] Mexican peso
* [MYR] Malaysian ringgit
* [MZN] Mozambican metical
* [NIO] Nicaraguan córdoba
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
