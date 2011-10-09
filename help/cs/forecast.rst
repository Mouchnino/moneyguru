Předpovědi
==========

Některé transakce, jako výplata, platby za služby, nájem, půjčky, se pravidelně opakují. To jsou vhodní kandidáti pro **naplánování**. Výši jiných výdajů - na potraviny, oblečení, jídlo v restauracích - můžete odhadnout. To jsou vhodní kandidáti pro **rozpočet**. Díky tomu, že moneyGuru disponuje plánováním výdajů a tvorbou rozpočtů, můžete předvídat svoji finanční situaci.

Jak to funguje
--------------

Jak plány, tak rozpočty pracují se systémem "událostí". Když vytváříte plán nebo rozpočet (v pohledech Plány a Rozpočty), vytváříte "vzorovou" transakci. Z této vzorové transakce se budou v pravidelných intervalech vytvářet události (podle toho, jak je definujete ve své vzorové transakci) a zobrazovat se v pohledech Transakce a Účet.

Plánované události můžete z pohledů Transakce a Účet přímo editovat. Po úpravě události se vás moneyGuru dotáže na rozsah platnosti úpravy. Můžete upravit pouze tuto jedinou událost (když například zaplatíte jednorázově větší splátku půjčky) nebo můžete provést globální změnu, která ovlivní všechny budoucí události (když se vám například zvýší nájemné).

Když měníte vzorovou transakci, ovlivní změny všechny výskyty *kromě* těch, které jste upravili ručně.

Rozpočty se chovají trochu jinak. Nelze je editovat, jejich částku ovlivňují jiné transakce. Transakce, které ovlivňují cílový příjmový/výdajový účet rozpočtu sníží k datu konce platnosti rozpočtu částku určenou na pokrytí všech transakcí. Pokud například máte měsíční rozpočet "Ošacení" ve výši 1000 Kč a v červenci vytvoříte transakci, která na "Ošacení" odešle 200 Kč, bude k 31. červenci výše rozpočtu "Ošacení" 800 Kč místo 1000 Kč.

Další zvláštností rozpočtových událostí je, že jsou výhradně *v budoucnosti*. Jakmile je dosažené datum konce platnosti rozpočtu, zmizí.

Vytváření plánu
---------------

Plánovanou transakci vytvoříte tak, že v pohledu Plány klepnete na tlačítko Nová položka. Objeví se panel Informace o plánu. Tento panel je podobný panelu Informace o transakci, má jen pár políček navíc: Typ opakování, Opakovat po, a Datum ukončení. Pole Typ opakování určuje interval mezi platbami (denně, týdně, atd.). Pole Opakovat po říká kolik intervalů má uplynout mezi každou platbou. Pokud například chcete platbu provádět jednou za 14 dní, nastvíte Typ opakování na Týdně a Opakovat po na 2.

Pokud už máte "vzorovou transakci", ze které chcete vytvořit plán, najdete v menu pro tuto operaci rychlou volbu - Vytvořit plán z výběru. Tím vytvoříte nový plán a informacemi z vybrané transakce předvyplníte všechny jeho údaje.

Všechny budoucí události u vytvořeného plánu se ve vybraném časovém rozmezí zobrazují s malou ikonou |clock|, která oznamuje, že se jedná o plánovanou transakci.

Úpravy plánu
------------

Kromě toho, že můžete upravovat plánované transakce v pohledu Plány, můžete také upravovat *kteroukoli událost* v pohledech Transakce nebo Účet. Události lze upravovat jako jakoukoli jinou transakci, ale může se vám hodit pár triků s klávesou Shift, kterými můžete ovládat plán.

* **Úprava pouze jedné události:** Pokud změníte událost jako byste měnili normální transakci, vytvoříte výjimku v plánu. Provedené změny bude obsahovat pouze tato událost.
* **Úpravy všech budoucích událostí:** Někdy můžete chtít změnit plán od určitého data až do konce. To provedete tak, že na konci prováděných úprav stisknete klávesu Shift. Tak se změní všechny plánované budoucí události.
* **Přeskočit událost:** Plánujete 2 měsíce neplaceného volna? Prostě smažte budoucí události ve vašem plánu pro mzdu, jako by šlo o normální transakci.
* **Ukončit plán:** Ne všechny plány jsou bez konce. Chcete-li ukončit plán k určitému datu, vyberte událost nejblíže následující po poslední plánované a smažte za současného držení klávesy Shift. Tím se smažou všechny budoucí události.

Jak vidíte, koncept je vcelku prostý: Plánované transakce můžete upravovat jako ostatní transakce, ale pokud stisknete klávesu Shift, změny se promítnou na všechny budoucí události v plánu.

**Kdy se událost stane:** Plánování transakcí je hezké, ale jednou také musejí nastat. V moneyGuru "nastanou", když transakci spárujete. Když naplánovanou transakci spárujete, stane se z ní normální transakce (zmizí u ní |clock| a už jí nelze použít ke změně budoucích událostí v plánu).

Tvorba rozpočtu
---------------

Rozpočet můžete vytvořit v pohledu Rozpočty. Pole Opakování fungují stejně jako u plánů. Pole Účet určuje příjmový nebo výdajový účet, pro který vytváříte rozpočet (Ošacení, Mzda, atd.). Ve volitelném poli Cíl, můžete určit majetkový nebo závazkový účet, který bude protistranou transakce. Když nějaký uvedete, bude v grafu zůstatku jeho "budoucí" část odrážet změny zůstatku, které nastanou.

Je důležité si uvědomit, že nastavení účtu Cíl **neomezuje** váš rozpočet jen na tento cílový účet. Vytvoříte-li například rozpočet "Ošacení" ve výši 2000 Kč, jako cíl nastavíte "Běžný účet" a potom prostřednictvím účtu "Kreditní karta" nakoupíte oděvy za 500 Kč, výše zbývajících prostředků pro daný měsíc se správně sníží na 1500 Kč.

Obvykle je nejlepší jako cíl pro rozpočet použít váš běžný účet, protože odtud peníze stejně většinou pocházejí a tam většinou přicházejí. Účelem cíle v rozpočtu je umožnit rozpočtu ovlivňovat váš budoucí zůstatek. Pokud například jako cíl vyberete účet svojí kreditní karty, pak pokud nenaplánujete transakce, které na ní budou pravidelně splácet dluh, bude budoucí zůstatek na kartě do nekonečna klesat.

Integrace s aplikací Cashculator
--------------------------------

**Tato funkce vyžaduje Cashculator v. 1.2.2 a pozdější.**

Pokud už víte jaké rozpočty chcete mít, jsou funkce pro tvorbu rozpočtu a plánů v moneyGuru dostatečné. Ale moneyGuru vám neumožní vymýšlet hypotetické rozpočty, abyste si navrhli takový, který budete dodržovat. Existuje hezká aplikace, `Cashculator <http://www.apparentsoft.com/cashculator>`__ , od jiného tvůrce, která se přesně na toto specializuje.

moneyGuru umí s Cashculatorem spolupracovat a usnadnit vám tak export "reálných" (v terminologii Cashculatoru) dat do této aplikace, návrh rozpočtů a jejich import do moneyGuru. Chcete-li tuto integraci využít, postupujte následovně:

1. Stáhněte si Cashculator, spusťte ho (aby se vytvořila kostra databáze, kterou moneyGuru potřebuje) a ukončete ho.
2. Otevřete si svá data v moneyGuru, otevřete novou záložku a klepněte na tlačítko "Cashculator".
3. Zobrazí se záložka se seznamem vašich příjmových a výdajových účtů. V tomto seznamu musíte vybrat, které účty jsou Cyklické a které jsou Necyklické (to je pro Cashculator důležitý rozdíl).
4. Klepněte na tlačítko "Exportovat účty". Vyexportují se všechny vaše příjmové a výdajové účty a pohyby peněz za poslední 4 měsíce. Nemějte obavy o svá data z Cashculatoru. moneyGuru vytváří vlastní kopii databáze Cashculatoru a data exportuje do ní.
5. Ujistěte se, že Cashculator není spuštěný a klepněte na tlačítko "Spustit Cashculator". Cashculator musíte tímto způsobem, protože tak Cashculator použije databázi připravenou moneyGuru, namísto své vlastní.
6. V Cashculatoru najdete scénář nazvaný "moneyGuru", kde budou všechny vaše účty a reálná data za poslední 4 měsíce. Použijte tyto údaje pro návrh rozpočtu (konzultujte dokumentaci Cashculatoru pro postup).
7. Jakmile máte hotovo, můžete podle svého návrhu vytvořil rozpočty a plány v moneyGuru. To musíte provést ručně, ale jedná se pouze o dočasné omezení této funkce (viz níže).
8. Po ukončení moneyGuru se Cashculator vrátí do normálního režimu (ke své standardní databázi).

**Integrace s Cashculatorem prozatím funguje pouze jednosměrně (export).** Caschulator funguje jinak než moneyGuru. Export dat do něj není nijak složitý, ale když se z něj mají importovat rozpočty zpátky do moneyGuru, není to tak lehké. V Cashculatoru lze vyplnit pole "Plán" mnoha různými způsoby. Není žádný jednoznačný postup, jak je automaticky konvertovat do rozpočtů a plánů.