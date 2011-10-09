Základy práce s moneyGuru
=========================

moneyGuru vychází z principů `podvojného účetnictví`_. Základem systému je **transakce** - přesun peněz z určitého účtu (nebo účtů) na jiný účet (nebo jiné účty) k určitému datu. Transakcí je sada dvou nebo více záznamů na dvou nebo více účtech, jejichž součtem je nula. Z jakéhokoli účtu, který reprezentuje majetek nebo příjem, lze odeslat peníze na jakýkoli jiný účet. To je užitečné v případě :doc:`správy hotovosti <cash>`. To je vše zásadní, co se dá říct k základům účetního systému. O něco složitější je situace v případě práce s více měnami. Detail naleznete na :doc:`stránce o měnách <currencies>`.

Záložky a pohledy
-----------------

Základem moneyGuru jsou různé pohledy (ty zásadní jsou vysvětleny níže). Přes pohledy spravujete data v moneyGuru. Pohledy samotné se spravují pomocí záložek. Záložky fungují stejně jako v každé aplikaci, která je používá. Záložku otevřete pomocí |cmd|\ T, zavřete ji stiskem |cmd|\ W, a mezi nimi se přesouváte klávesovými zkratkami |cmd_shift|\ ←→. Kdykoli otevřete účet pomocí šipky |basics_show_account_arrow|, otevře se pro něj nová záložka (nebo pokud už byl účet otevřen, aktivuje se jeho záložka).

Časové rozmezí
--------------

Aktuálně vybrané časové rozmezí je platné pro celou aplikaci. Vše co je v pohledu vidět, platí pro aktuálně vybrané časové rozmezí. Pokud je například vybráno rozmezí "Led 2010 - Pro 2010" vidíte ve všech pohledech údaje od 1.1.2010 do 31.12.2010. Časové rozmezí nastavujete tímto prvkem:

|basics_date_range|

Program pracuje se 7 druhy časového rozmezí:

#. **Měsíc:** Začíná prvního dne a končí posledního dne stejného měsíce.
#. **čtvrtletí:** Začíná v první den čtvrtletí (3 měsíce) a končí jeho poslední den.
#. **Rok:** Začíná 1. ledna a končí 31. prosince.
#. **Aktuální rok:** Začíná 1. ledna *letošního* roku a končí *dnes*. Tento rozsah použijte, pokud chcete, aby vám moneyGuru ukázal vaší současnou situaci (bez naplánovaných transakcí a bez budoucích transakcí podle rozpočtu).
#. **Probíhající rok:** Toto rozmezí *se odvozuje* od aktuálního data. Zobrazuje se přesně *jeden rok*, ale ne kalendářní. Pro určení konce časového rozsahu se používá předvolba "Měsíců napřed v probíhajícím roce". Začátek rozsahu je přesně jeden rok před tímto datem.
#. **Všechny transakce:** Počátkem časového rozmezí je nejstarší zaznamenaná transakce ve vašem dokumentu. Konec je nastaven na přítomnost + měsíce napřed (viz Probíhající rok).
#. **Uživatelské časové rozmezí:** V tomto případě si moneyGuru vyžádá počáteční a koncové datum. Ty budou představovat hranice časového rozmezí.

U "pevných" časových rozmezí (Měsíc, Čtvrtletí, Rok) můžete pomocí šipek vybírat předchozí nebo následující období (na klávesnici můžete využít |cmd_opt|\ [ a |cmd_opt|\ ]). Také můžete pro výběr různých druhů časových rozmezí použít klávesové zkratky (|cmd_opt|\ 1-7). Stiskem kláves |cmd_opt|\ T se vrátíte ke zobrazení časového rozmezí, které zahrnuje dnešek.

Při definování uživatelského časového rozmezí si ho také můžete uložit do jedné ze 3 dostupných předvoleb. Pokud tak učiníte, objeví se nové časové rozmezí v menu a bude možné ho rychle vybrat.

Červená linka
-------------

moneyGuru zobrazuje všechny informace podle aktuálně vybraného časového rozmezí. To je zajímavé, pokud časové rozmezí končí v budoucnu. Pokud máte naplánované transakce nebo vytvořený rozpočet, budou zahrnuté v grafech nebo číslech, na které se budete dívat. V grafech je minulost a budoucnost jasně odlišena. Minulost je zobrazena zeleně, budoucnost šedě. Odděluje je tenká červená linka. Pokud se tedy díváte na šedou část grafu, díváte se na transakce, které ještě neproběhly. Čisté jmění v rozvaze bude zahrnovat doposud neproběhlé naplánované transakce a transakce podle rozpočtu. Někdy vás zajímá pouze vaše aktuální finanční situace. K tomu je určeno časové rozmezí "Aktuální rok" (|cmd_opt|\ 4).

Čisté jmění a Zisky a ztráty
----------------------------

|basics_net_worth|

Pohledy Čisté jmění a Zisky a ztráty vám poslouží při správě účtů a získání statistik o vaší finanční situaci. Mají podobné rozvržení a i se podobně chovají.

**Přehled:** Vlevo nahoře je "přehled", najdete tu seznam účtů a součty za jednotlivé skupiny účtů. Součty jsou vždy uvedeny ve vaší domácí měně. Z přehledu také můžete účty :doc:`přidat, upravit a smazat <editing>`.

**Zobrazit účet:** U každého účtu je malá značka |basics_show_account_arrow|. Klepnutím na ní zobrazíte pohled na daný účet. Také můžete aktivovat řádek s názvem účtu a stisknout |cmd|\ →.

**Vyloučení účtu:** Účty můžete "vyloučit" klepnutím na ikonu |basics_account_out| nebo stisknutím klávesové zkratky |cmd_shift|\ X. Vyloučené účty se nezapočítávají do součtů v přehledu ani do grafů.

**Koláčový graf:** V pravé části obou pohledů jsou dva koláčové grafy, které zobrazují váhu každého účtu v dané kategorii. Pokud používáte skupiny účtů, můžete takovou skupinu v přehledu sbalit a sloučit hodnoty jejích jednotlivých účtů do jedné hodnoty v koláčovém grafu. Pokud například máte skupinu účtů "Automobil" a v ní několik souvisejících účtů, můžete v přehledu skupinu sbalit a v grafu se objeví jedna výseč nazvaná "Automobil" (místo abyste měli jednu výseč pro Benzín, další pro Pojištění, atd.)

**Graf:** Graf v dolní části pohledu ukazuje vývoj hlavní zobrazované statistiky pohledu (čisté jmění nebo zisk) v čase.

**Sloupce:** Každý přehled má vlastní sadu sloupců (které si lze přizpůsobit po stisku  |cmd|\ J).

* **Rozvaha:**

    * **účet č.:** volitelný číselný odkaz spojený s účtem. Pro více informací viz :doc:`stránka editace <editing>`.
    * **Start:** Zůstatek na účtu na začátku časového rozmezí. Zahrnuje plánované transakce, ale ne rozpočty.
    * **Konec:** Zůstatek na účtu na konci časového rozmezí.
    * **Změna:** Rozdíl mezi body Start a Konec.
    * **Změna %:** Rozdíl mezi body Start a Konec v procentech.
    * **V rozpočtu:** Částka rozpočtu (pro který tento účet představuje **cíl**), kterou lze ještě v daném časovém rozmezí využít. Pokud vaše rozpočty odpovídají realitě, měl by součet hodnot Konec + V rozpočtu představovat váš skutečný zůstatek na konci časového rozmezí.
    
* **Zisky a ztráty:**

    * **účet č.:** Stejný význam jako v Rozvaze.
    * **Aktuální:** Pohyb hotovosti na účtu na začátku aktuálního časového rozmezí.
    * **Poslední:** Pohyb hotovosti na účtu v předchozím časovém rozmezí. Pokud je nyní například březen, pak u měsíčního rozmezí zobrazuje sloupec Poslední pohyb hotovosti v měsíci únoru. Rozmezí Aktuální rok je zvláštním případem, v tom případě sloupec Poslední zobrazuje pohyb hotovosti za loňský rok.
    * **Změna a Změna %:** Stejný význam jako v Rozvaze.
    * **V rozpočtu:** Částka rozpočtu přidělená k danému účtu, kterou lze ještě v aktuálním časovém rozmezí čerpat. Pokud vaše rozpočty odpovídají realitě, měl by součet hodnot Aktuální + V rozpočtu představovat váš skutečný pohyb hotovosti pro daný účet na konci časového rozmezí.

Transakce
---------

|basics_transactions|

Pohled Transakce zobrazuje všechny transakce obsažené v dokumentu pro dané časové rozmezí. Zde můžete transakce také :doc:`přidat, upravit a smazat <editing>`. Tento pohled je nejefektivnější pro vkládání dávek transakcí (například pokud máte hromadu faktur a účtenek). **Částka** určuje hodnotu transakce. **Z** a **Na** obsahují názvy účtů, jichž se transakce týká (pokud jde o dělenou transakci, jsou názvy odděleny čárkou). Tyto 3 sloupce říkají, že "Tato transakce bere **Částku** z účtu **Z** a přesouvá ji na účet **Na**". Pokud je například účet **Z** "Běžný účet" a **Na** je "Jídlo", znamená to, že jsou z Běžného účtu vybrány peníze a jsou vydány za Jídlo. Příjem se zaznamená tak, že účet **Z** bude "Plat" a účet **Na** bude "Běžný účet".

Nad seznamem transakcí je **lišta s filtry**, kde můžete ovlivňovat viditelnost určitých typů transakcí.

* **Příjem:** Zobrazí se pouze transakce, které ovlivnily alespoň jeden příjmový účet.
* **Výdaj:** Zobrazí se pouze transakce, které ovlivnily alespoň jeden výdajový účet.
* **Přesun:** Zobrazí se pouze transakce, které ovlivnily alespoň dva účty aktiv nebo závazků.
* **Nepřiřazeno:** Zobrazí se pouze transakce, které mají alespoň jeden nepřiřazený záznam.
* **Spárované:** Zobrazí se pouze transakce, které mají alespoň jeden spárovaný záznam.
* **Nespárované:** Zobrazí se pouze transakce, které mají alespoň jeden nespárovaný záznam.

Buňky **Z** a **Na** mají po pravé straně malou ikonu |basics_show_account_arrow|. Podobně jako u pohledů Čisté jmění a Zisky můžete klepnutím na ni zobrazit účet, kterého se záznam transakce týká (pokud je transakce rozdělena mezi více účtů, zobrazí se ten první z nich).

Účet
----

|basics_account|

Tento pohled zobrazuje transakce *z perspektivy určitého účtu*. Pohled na účet otevřete klepnutím na |basics_show_account_arrow| v jiném pohledu. Zobrazí se seznam transakcí podobně jako v pohledu Transakce, ale zde jsou pouze transakce, které mají vztah ke zobrazovanému účtu. Místo sloupců **Z** a **Na** tu je pouze sloupec **Přesun** (*druhá strana* transakce). Zato sloupec **Částka** je rozdělen na sloupce **Vklad** a **Výběr**. Pokud se například dívám na Běžný účet, ve sloupci **Přesun** je "Jídlo" a ve sloupci **Výběr** je "42", znamená to, že jsem z Běžného účtu vybral 42 Kč a přesunul je na účet Jídlo. Pokud je zobrazený účet aktiv nebo závazků, je navíc vidět i sloupec **Zůstatek**, kde je aktuální zůstatek na účtu. Graf ve spodní části okna zobrazuje zůstatek účtu pro každý den časového rozmezí. Pokud je zobrazen účet z kategorie příjem nebo výdaj, zobrazí se podobný sloupcový graf jako je v pohledu Zisky a ztráty.

Pohled na účet je také vybaven lištou s filtry. Ta se chová podobně jako ta v pohledu Transakce, ale jsou tu malé rozdíly.

* **Vklad:** Zobrazí se pouze položky, u nichž je částka na straně "Vklad".
* **Výběr:** Zobrazí se pouze položky, u nichž je částka na straně "Výběr".
* **Přesun:** Zobrazí se pouze transakce, které jsou součástí transakce, která ovlivnila alespoň dva účty aktiv nebo závazků.
* **Nepřiřazeno:** Zobrazí se pouze nepřiřazené transakce.
* **Spárované:** Zobrazí se pouze spárované transakce.
* **Nespárované:** Zobrazí se pouze nespárované transakce.

Tlačítko *Párování* v liště s filtry (aktivní pouze u aktiv/závazků) vám umožní přepínat aktivaci režimu :doc:`párování <reconciliation>`.

Buňky **Přesun** mají po pravé straně malou ikonu |basics_show_account_arrow|. Podobně jako v jiných pohledech klepnutím na ni zobrazíte účet spojený s touto buňkou. Na rozdíl od šipek v pohledu Transakce zde pouze *procházíte dokola* dělenou transakcí. I když je transakce rozdělena na více než dva účty, opakované klepání na šipku zobrazí všechny dotčené účty, nikoli jen první dva.

V závislosti na vybraném časovém rozmezí může být na prvním řádku tabulky položka **Předchozí zůstatek**. Tato položka, podobně jako u výpisu z účtu, ukazuje zůstatek na účtu na začátku časového rozmezí.

Účetní kniha
------------

V tomto pohledu jsou sloučeny všechny účty a zobrazeny všechny záznamy za aktuální časové rozmezí. Záznamy jsou prezentovány velmi podobně jako v pohledu Účet. Tento pohled slouží především pro reportovací účely.

Filtrování
----------

Pole pro zadání filtru v nástrojové liště vám umožňuje zobrazit ty transakce, které odpovídají zadanému výrazu. Chcete-li filtrovat transakce, napište něco do pole potvrďte stiskem klávesy Enter. V seznamu transakcí se zobrazí pouze ty, jejichž popis, příjemce, číslo šeku, název účtu nebo částka odpovídá napsanému výrazu. Pokud chcete vidět pouze transakce z určitých účtů nebo skupin účtů napište do pole pro zadání filtru "účet: účet1,účet2" nebo "skupina: skupina1,skupina2". To je velmi užitečné pro :doc:`hromadné úpravy <editing>`.

Možnosti zobrazení
------------------

|basics_view_options|

moneyGuru má panel Nastavení zobrazení, kde můžete skrýt některé prvky (jako např. grafy). Zobrazíte ho (a zase schováte) klávesovou zkratkou |cmd|\ J.

Co Vidíte To Vytisknete (víceméně)
----------------------------------

moneyGuru vám umožní vytisknout cokoli právě vidíte v kterémkoli ze čtyř pohledů. Přejete si vytisknout seznam transakcí za minulý rok? Nastavte časové rozmezí na minulý rok, přepněte se do pohledu Transakce a stiskněte |cmd|\ P. moneyGuru automaticky přizpůsobí šířku sloupců jejich obsahu (sloupce s delšími údaji budou širší) a pokusí se rozvrhnout údaje tak, aby se vešly na papír.

.. _podvojného účetnictví: http://en.wikipedia.org/wiki/Double-entry_bookkeeping_system