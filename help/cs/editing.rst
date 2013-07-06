Úpravy dokumentu moneyGuru
==========================

Základy
-------

V moneyGuru je několik klávesových zkratek a tlačítek, které mají stejnou funkci v jakékoli části programu. Začněme sadou tří tlačítek v levém dolním rohu:

|edition_buttons|

Tlačítko + něco nového vytváří, tlačítko - vybranou věc ruší a tlačítko *i* zobrazí informaci o vybrané věci. Co je tou "věcí" záleží na aktuálním pohledu. V rozvaze a Stavu příjmů je to účet. V pohledech Transakce a Účet to je transakce. Pokud vyberete více než jednu transakci a klepnete na tlačítko *i*, zobrazí se namísto panel s detaily transakce panel Hromadná editace.

Přirozeně lze téhož dosáhnout i s použitím klávesnice. |cmd|\ N vytváří něco nového, klávesy Delete a Backspace mažou vybranou věc a  |cmd|\ I zobrazí informaci o vybrané věci.

Vybranou věc lze upravovat poklepáním na editovatelnou buňku (například pole s názvem účtu). Úpravy je také možné zahájit vybráním dané věci a stisknutím klávesy Return. První editovatelná buňka se přepne do režimu úprav.

V tomto režimu lze stiskem kláves Tab a Shift-Tab přecházet mezi modifikovatelnými buňkami. Pokud už v řádku nejsou další modifikovatelné buňky, editace končí. Úpravy také můžete ukončit opětovným stiskem klávesy Return. Úpravy zrušíte stiskem klávesy Escape. Všechny provedené změny v právě upravovaném řádku budou ztraceny a nahrazeny původními hodnotami.

Účty
----

Účty se upravují z Rozvahy a Stavu příjmů. Když vytvoříte nový účet, bude toho typu, kde právě byl váš výběr. Pokud mám vybraný účet "Kreditní karta" a stisknu |cmd|\ N, vytvořím nový účet závazků. Následně můžete zapsat název účtu a stiskem klávesy Return ukončíte editaci.

Pomocí drag & drop můžete změnit typ účtu nebo ho zařadit do skupiny (apropos, skupina účtů -  novou vytvoříte stiskem klávesové zkratky |cmd_shift|\ N).

|edition_account_panel|

Příkaz Zobrazit informace u účtu zobrazí editační panel jako na obrázku. Zde můžete upravit název účtu, ale také změnit jeho typ, jeho :doc:`měnu <currencies>` a jeho číslo. Číslo účtu je numerický odkaz na účet. Použijte ho, pokud ve svém účetnictví používáte čísla účtů (například 1000-1999 pro majetek, 8000-8999 pro výdaje). Má-li účet číslo účtu, zobrazí se spolu s jeho názvem v pohledech Transakce a Účet. Navíc můžete zapsat číslo účtu místo jeho názvu v odkazech na daný účet (pokud ho znáte zpaměti, čímž zrychlíte zápis).

Ohledně účtů a měn: Měnu můžete změnit pouze u účtu, který nemá žádnou :doc:`spárovanou položku <reconciliation>`. Pokud z nějakého důvodu chcete změnit měnu u účtu se spárovanými položkami, musíte nejprve zrušit párování jeho položek. Mějte na paměti, že změna měny účtu **nezmění** měnu provedených transakcí.

Transakce
---------

Transakce lze upravovat z pohledů Transakce a Účet. Při vytváření nové transakce se jako její datum použije datum právě vybrané transakce (viz "Úprava data" níže ). Sloupce Popis, Příjemce a Účet (Z, Na Přesun) se automaticky doplňují (viz "Automatické doplňování" níže).

Je možné změnit pořadí transakce v rámci skupiny transakcí provedených ve stejném dni. To provedete pomocí drag & drop, nebo použijte klávesové zkratky |cmd|\ + a |cmd|\ -.

Pokud ve sloupci Účet zapíšete název účtu, který ještě neexistuje, tento účet se automaticky vytvoří jako příjmový nebo výdajový účet (v závislosti na částce v transakci). Nemějte obavy, že byste překlepy vytvořili kvanta účtů, které pak budete muset pročistit. Pokud opravíte překlep v transakci, automaticky vytvořený účet se i automaticky odstraní.

|edition_transaction_panel|

Pokud na jediné transakci vyvoláte příkaz Zobrazit informace, objeví se tento panel. V něm můžete upravovat totéž, co lze v pohledech Transakce a Účet. Navíc tu můžete pomocí tabulky ve spodní části panelu vytvářet a upravovat transakce s více než dvěma položkami (obvykle nazývané "Dělené transakce").

Jednu věc je třeba mít u této tabulky stále na paměti - transakce se tu automaticky vyrovnává. Takže pokud tu v transakci prostě smažete jednu z jejích položek, transakce nezmizí. Ihned se do ní přidá položka nespojená se žádným účtem ve stejné výši. Změna částky v položce také automaticky přidá položku nespojenou se žádným účtem na částku rovnou rozdílu mezi původní a novou částkou. Řekněme, že například chcete zaúčtovat dělenou transakci, kdy vám spolubydlící uhradil část účtu na 400 Kč (třeba za internet), který jste zaplatili bankovním převodem a spolubydlící vám dal 200 Kč v hotovosti. Provedete to následovně:

#. Zadejte normální podvojnou transakci Běžný účet --> Služby.
#. Pro transakci vyvolejte panel Zobrazit informace.
#. Změňte na účtu Služby výběr na 200 Kč. Vznikne třetí řádek bez přiřazení k účtu s výběrem 200 Kč.
#. Změňte účet u třetího řádku na Hotovost.

|edition_three_way_split|

Skvělé, právě jste vytvořili třícestnou dělenou transakci. Tato transakce přesně odráží realitu, kdy 400 Kč odešlo z vašeho běžného účtu, internet vás ve skutečnosti stál 200 Kč a v kapse se vám navíc objevilo 200 Kč.

|edition_mass_edition_panel|

Použití panelu Zobrazit informace pro více než jednu vybranou transakci vyvolá panel podle obrázku nahoře. Ten vám umožní provést hromadné úpravy. Po klepnutí na Uložit se u všech vybraných transakcí změní atributy, u kterých jsou aktivní zatržítka na hodnoty z polí vedle těchto zatržítek.

Editace data
------------

Editace data se provádí ve speciálním poli. Pole má tři části: den, měsíc a rok. Po zahájení úprav je vždy vybrána část **den**, bez ohledu na používaný formát data. Mezi částmi pole se pohybujete šipkami vlevo a vpravo. Hodnotu v právě vybrané části pole můžete zvyšovat a snižovat šipkami nahoru a dolů. Samozřejmě také můžete datum zapsat přímo z klávesnice. Pole automaticky mění vybranou část při zápisu oddělovače data nebo dosažení maximální délky zápisu pro danou část. Vše objasní následující seznam pravidel, kterými se datové pole řídí:

* Formát zobrazení data vždy odpovídá formátu, který používá váš systém.
* **Vstupní** formát je vždy den --> měsíc --> rok.
* Ať v systému používáte jakýkoli formát zobrazení, můžete datum zapsat s nulou na začátku. Pokud například používáte formát data mm/dd/yy můžete datum "07/06/08" zapsat jako "060708".
* Ať v systému používáte jakýkoli formát zobrazení, můžete datum zapsat pomocí oddělovačů. Pokud například používáte formát data yyyy-mm-dd můžete datum "2008-07-06" zapsat jako "6-7-08".

Pokud při úpravách transakce nebo položky zapíšete datum, které je mimo aktuální časové rozmezí, objeví se |backward_16| nebo |forward_16|. To znamená, že pokud lze vaším zvoleným časovým rozmezím procházet (Měsíc, Čtvrtletí, Rok), přizpůsobí se dané rozmezí po skončení úprav tak, aby se v něm zobrazila upravená transakce. Pokud nelze zvoleným časovým rozmezím procházet (Aktuální rok, Probíhající rok, Vlastní) zmizí upravovaná transakce z aktuální pohledu.

Editace částky
--------------

Pole, do kterých můžete zadávat částky mají několik skrytých vlastností. 

*Můžete do nich zadávat jednoduché výrazy jako "2+4.35/2", které budou automaticky vyhodnoceny.
* Pokud máte aktivní předvolbu "Automaticky umísťovat desetinnou čárku při zápisu", pak zápis čísla bez desetinné čárky povede k tomu, že se desetinná čárka do čísla automaticky umístí. Pokud například máte jako výchozí měnu USD, pak zápis "1234" znamená částku "12.34".
* Vždy můžete explicitně uvést měnu dané částky tím, že na před nebo za ní zapíšete třípísmenný kód měny podle ISO (viz :doc:`stránka nápovědy k měnám <currencies>`). 

Automatické dokončování, automatické vyplňování a vyhledávání
-------------------------------------------------------------

moneyGuru obsahuje pokročilé funkce automatického dokončování a vyplňování. Jakmile něco zapíšete do pole, kde je možné automatické dokončování (Popis, Příjemce, Účet), moneyGuru prohledá ostatní transakce a nabídne vám návrhy na dokončení. Seznamem nabídek můžete procházet pomocí šipek nahoru a dolů. Nabízenou položku přijmete stiskem tabelátoru. Také můžete pokračovat v zápisu.

Automatické vyplňování samo vyplní prázdná políčka poté, co tabelátorem vyplníte pole s aktivním automatickým dokončováním. Řekněme, že Příjemce je prvním sloupcem, kde lze automaticky dokončit zápis. Zapíšete-li existujícího příjemce, všechna další pole se automaticky naplní hodnotami z poslední transakce s tímto příjemcem.

V Mac OS X je možné pro každé pole s automatickým dokončováním vytvořit seznam pro vyhledání. Potřebujete zapsat příjemce, o kterém **víte**, že ho někde v transakcích máte, ale nepamatujete si jak začíná jeho jméno? Stiskněte |cmd|\ L a objeví se prohledávací dialog se seznamem všech příjemců. Můžete zde vyhledávat i na základě části názvu příjemce (část může být kdekoli v názvu). Nejpravděpodobnější příjemci se objeví na vrcholu seznamu.

.. |edition_buttons| image:: image/edition_buttons.png
.. |edition_account_panel| image:: image/edition_account_panel.png
.. |edition_transaction_panel| image:: image/edition_transaction_panel.png
.. |edition_three_way_split| image:: image/edition_three_way_split.png
.. |edition_mass_edition_panel| image:: image/edition_mass_edition_panel.png
.. |backward_16| image:: image/backward_16.png
.. |forward_16| image:: image/forward_16.png
