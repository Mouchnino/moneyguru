Import dat do moneyGuru
=======================

moneyGuru podporuje import ze souborových formátů QIF, OFX, QFX a CSV. Soubor importujete tak, že v menu "Soubor" vyberete položku "Import..." a vyberete importovaný soubor. Zobrazí se následující okno:

|import_window|

Pro každý účet, který je v importovaném souboru se v tomto okně objeví záložka. Použití tohoto dialogového okna je poměrně jednoduché. Sloupec vlevo se zaškrtávacím tlačítkem určuje, které transakce se budou importovat. Zkontrolujte importované transakce, zrušte zaškrtnutí u těch, které importovat nechcete a klepněte na tlačítko Import. Naimportuje se pouze jeden účet (ten, který je vybraný).

Oprava data
-----------

moneyGuru automaticky identifikuje formát data použitý v importovaném souboru. Vybírá takový formát data, který je smysluplný pro všechny zapsaná data. Importované soubory ale někdy mohou obsahovat nejednoznačná data (jako "01/02/03), ze kterých moneyGuru nemůže s určitostí stanovit formát data. V takovém případě moneyGuru zvolí první formát, který vyhovuje. Co si počít, pokud vybere špatný formát? Použijte tlačítko Prohodit! Pokud například moneyguru vybere pro vás soubor formát dd/mm/yy, ale ve skutečnosti jde o formát mm/dd/yy, vyberte v horním pravém rohu "Den <--> Měsíc" a klepněte na tlačítko Prohodit. Prohození můžete aplikovat na všechny účty v okně Import. V takovém případě před prohozením zaškrtněte volbu "Použít pro všechny účty".

Prohození popisu a příjemce
---------------------------

V některých případech jsou zaměněna pole popis a příjemce. Mohlo se tak stát v důsledku omylu v aplikaci, která vytvořila importní soubor, kvůli nejednoznačnosti souborového formátu, nebo z jakéhokoli jiného důvodu. Na příčině nezáleží, protože to můžete napravit v okně Import. Stačí vybrat v rozbalovacím seznamu "Popis <--> Příjemce a stisknout tlačítko "Prohodit". A je to.

.. todo:: Update the 2 section below with the new "Fix broken fields" section.

Import do existujícího účtu
---------------------------

Standardně se transakce importují do nového účtu. Pokud ale chcete, můžete transakce naimportovat do existujícího účtu tak, že změníte cílový účet. Když importujete OFX soubory, vybírá se cílový účet automaticky, pokud je to vhodné. Pokud vyberete cílový účet, takto nepatrně se změní tabulka pro přiřazení:

|import_match_table|

Změna je proto, že při importu do existujícího účtu je možné, že importujete i transakce, které už máte zaznamenané. Musíte moneyGuru sdělit, které transakce patří ke kterým. Pokud importujete OFX soubor, toto se děje automaticky, ale stále máte možnost ručně změnit přiřazení.

Na levé straně tabulky (první 3 sloupce) jsou :doc:`nespárované <reconciliation>` transakce z cílového účtu. Na pravé straně jsou transakce, které se budou importovat. Nepřiřazené transakce mají jednu stranu prázdnou. Přiřazené transakce mají obě strany vyplněné a uprostřed mají ikonu zámku. Klepnutím na zámek můžete rozdělit již přiřazené transakce. Pomocí drag & drop můžete transakci přiřadit k další.

Pokud importujete OFX soubor do účtu, kam jste již dříve importovali z OFX, děje se to automaticky. Je tu ale výjimka z pravidla, že vlevo se zobrazují pouze nespárované transakce. Pokud je transakce v importovaném OFX souboru přiřazena ke spárované transakci z cílového účtu, přenese se. Zaškrtávací pole indikující import ale nebude zaškrtnuto (standardně je zaškrtnuté). Důvodem pro toto chování je, že pokud máte transakci spárovanou, zřejmě nechcete tento stav měnit.

Import CSV
----------

Import CSV souboru je stejný jako import jiného typu souboru, ale než se dostanete do hlavního okna importu, musíte moneyGuru sdělit, co který sloupec v CSV souboru znamená.

|import_csv_options|

Problémem CSV je, že neexistuje vůbec žádný standard týkající se struktury souboru. V tomto okně moneyGuru řeknete, jaký sloupec má jaký význam. Prohlédněte si zobrazené údaje a když identifikujete význam sloupce (například datum), klepněte na záhlaví daného sloupce a přiřaďte vhodné pole transakce. Povinné jsou sloupce Datum a Částka.

CSV soubory mají často řádky záhlaví (a někdy i zápatí). moneyGuru dopředu neví, co které řádky znamenají. Proto musíte sami zrušit zaškrtnutí u každého sloupce a řádku, které neidentifikují transakci.

Někdy jsou CSV soubory natolik podivné, že moneyGuru nedokáže správně určit oddělovač jednotlivých polí. Pokud se to stane, budete mít ve sloupcích podivná data. Půlka hodnoty bude v jednom sloupci a druhá půlka bude v jiném. V takových případech použijte pole **Oddělovač**, kde ručně určíte oddělovač polí pro daný CSV soubor. Pak klepněte na tlačítko "Přenačíst", aby se znovu načetli sloupce za použití určeného oddělovače.

moneyGuru si při ukončení ukládá informace o sloupcích a řádcích záhlaví. Pokud pravidelně importujete více typů CSV, můžete použít Rozvržení. Každé rozvržení ukládá vlastní konfiguraci sloupců a záhlaví.

V okně voleb CSV Je také možné přímo určit cílový účet. Funkce je stejná jako když určíte cílový účet později v okně Import. Pokud ale cíl určíte v okně s volbami pro CSV, uloží se do rozvržení.
