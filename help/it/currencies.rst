Valute
======

moneyGuru ha un solido supporto per le valute multiple: ogni ammontare contiene la propria informazione di valuta, quindi qualsiasi somma può essere in una qualsiasi valuta. Sono stati fatti molti sforzi per garantire che si capisca sempre in quale valuta è espressa una somma, senza affaticare la vista con un codice di valuta per ogni cifra.

.. todo:: Update from english version

Un elemento centrale in moneyGuru è che ci sono 2 tipi di valuta. La valuta **nativa** e le valute **straniere**. La valuta nativa è quella del sistema operativa. Le valute straniere sono tutte le altre.

Le valute vengono mostrate con una regola molto semplice: se l'ammontare è nella valuta nativa, è mostra senza codice, altrimenti è mostrato con il codice ISO a tre lettere della valuta (USD, CAD, EUR, GBP, etc..).

Le regole per l'inserimento delle somme è appena più complesso; nella maggior parte dei casi, digitando un numero senza un codice di valuta significa che sarà nella valuta nativa. Comunque, se si è nella vista di un conto che non è impostato alla valuta nativa, inserendo una cifra senza codice di valuta, si intenderà la valuta di quel conto. La ragione è che se anche la vostra valuta nativa è ad esempio USD, quando si sta operando un conto in EUR è **molto** probabile che si vogliano inserire somme in EUR. Ovviamente, **in tutti i casi** è possibile inserire esplicitamente il codice di una valuta prima o dopo le cifre per ottenere l'ammontare in quella valuta.

Alcune altre applicazioni fanno una conversione automatica dell'ammontare di un trasferimento tra conti di diverse valute. Questo non ha molto senso, perché se prelevo 200 USD (dollari americani) da un bancomat durante un viaggio, l'ammontare che verrà detratto dal vostro conto sarà **certamente diverso** da quello calcolabile con il cambio del giorno. I tassi di cambio sono sempre delle stime e vanno trattate di conseguenza. In moneyGuru, la valuta di un ammontare rimane esattamente come è fino a che non lo si modifica diversamente; nel caso precedente, ad esempio dopo aver ricevuto l'estratto conto.

Anche se moneyGuru non usa i tassi di cambio per convertire le somme di una transazione, le utilizza per altre cose: patrimonio netto, guadagno e le stime del saldo corrente. In moneyGuru il proprio patrimonio netto o guadagno viene sempre mostrato nella valuta corrente. Se avete un conto in una valuta straniera, non è più possibile avere dei valori certi; in questi casi, moneyGuru recupera automaticamente i tassi per ogni data di transazione e li utilizza. Per il calcolo del saldo corrente, è possibile avere temporaneamente un'ammontare in valuta estera in una Attività o in una Passività. Fino a che non si riconcilia questa voce e la si cambia nella valuta naturale del conto, il saldo corrente sarà solo una stima.


Transazioni con più valute
--------------------------

La stragrande maggioranza delle transazione, anche se si utilizzano più valute, conterrà una sola valuta alla volta. Se si acquista un aggeggio su Ebay per 200 USD con la carta di credito, ad esempio creando una transazione Carta di Credito --> Aggeggi Vari per 200 USD, quando si riconcilia il conto Carta di Credito, quell'ammontare andrà sostituito con la somma in EUR che vi sarà stata addebitata corrispondentemente.

Tuttavia, se si fa un trasferimento tra un'Attività e una Passività tra conti in diverse valute, il discorso cambia. Se ad esempio si trasferiscono 100 EUR dalla propria banca ad un'altra banca con un conto in dollari USD, allora i due lati della transazione avranno valute diverse.

Questo è un problema spinoso perché i tassi di cambio sono delle stime e non c'è modo di avere un bilancio nullo per quella transazione, mentre come si sa, le transazioni devono sempre dare un bilancio nullo. Quindi si crea un'eccezione stabilendo per definizione che **una transazione tra due valute diverse sarà sempre bilanciata**. Nell'esempio sopra, si avrà quindi una transazione che addebita 100 EUR da una parte e accredita 150 USD dall'altra. 

Per creare transazioni con più valute è sufficiente andare nell'"altro lato" della transazione e inserire l'ammontare nella valuta desiderata. Si può anche utilizzare il pannello di modifica delle transazioni; per esempio, volendo aggiungere la transazione di prima, innanzitutto si va in Conto Corrente e si aggiunge una transazione di 100 EUR verso l'altro "Conto in Dollari". Quindi si va nel "Conto in Dollari" e si cambia l'ammontare di 100 EUR in 150 USD. moneyGuru capirà automaticamente che l'"altro lato" della transazione è un'Attività in una valuta diversa e che quindi i corrispondenti 100 EUR devono essere mantenuti tali e quali.

Anche se i tassi di cambio sono sempre delle stime, le banche e le compagnie delle carte di credito tendono sempre a darvi un tasso di conversione inferiore al reale nelle transazioni con più valute. Quindi, anche se le transazioni tra più valute sono sempre considerate bilanciate per definizione, a volte può tornare utile utilizzare il tasso di cambio per bilanciare realmente una transazione: questo può servire per esempio per valutare e registra la differenza tra il tasso di cambio effettivo e quello applicato dalla banca come una spesa. Questo è ciò a cui serve il pulsante **Bilancio Multi-valuta** nel pannello Info Transazione. Quando vi si fa click, una nuova voce verrà creata nella transazione con la differenza tra i "due lati" della transazione, utilizzando il tasso di conversione alla data.

Regole sulle valute
-------------------

* Un ammontare in una valuta estera è **sempre** mostrato esplicitamente con il codice ISO.
* Inserendo esplicitamente il codice ISO di una valuta per una certa cifra, si trasforma **sempre** questo ammontare nella valuta indicata.
* Inserendo una cifra senza codice, si ottiene un ammontare nella valuta nativa, eccezion fatta per:

    * la modifica di un conto in una valuta straniera.
    * la modifica di una transazione multipla in valuta straniera.

* Il Patrimonio Netto e il Guadagno sono sempre calcolati nella valuta nativa.
* Una transazione tra più valute è sempre bilanciata per definizione.

Valute supportate
-----------------

* [USD] Dollari U.S.A.
* [EUR] Euro
* [GBP] Sterlina Inglese
* [CAD] Dollari Canadesi
* [AUD] Dollari Australiani
* [JPY] Yen Giapponesi
* [INR] Rupia Indiana
* [NZD] Dollari Neozelandesi
* [CHF] Franchi Svizzeri
* [ZAR] Rand Sudafricano
* [AED] Dirham Emirati Arabi Uniti
* [ANG] Fiorino delle Antille Olandesi
* [ARS] Peso Argentino
* [ATS] Scellini Austriaci
* [BBD] Dollaro delle Barbados
* [BEF] Franchi Belgi
* [BHD] Dinaro del Bahrein
* [BRL] Real Brasiliano
* [BSD] Dollaro delle Bahamas
* [CLP] Peso Cileno
* [CNY] Yuan Renminbi Cinese
* [COP] Peso Colombiano
* [CZK] Corona Ceca
* [DEM] Marchi Tedeschi
* [DKK] Corone Danesi
* [EGP] Sterlina Egiziana
* [ESP] Peseta Spagnole
* [FIM] Markka Finlandese
* [FJD] Dollaro delle Fiji
* [FRF] Franchi Francesi
* [GHC] Cedi del Ghana (vecchio)
* [GHS] Cedi del Ghana (nuovo)
* [GRD] Dracme Greche
* [GTQ] Quetzal Guatemalteco
* [HKD] Dollari di Hong Kong
* [HNL] Lempira Onduregna
* [HRK] Kuna Croata
* [HUF] Fiorino Ungherese
* [IDR] Rupiah Indonesiana
* [IEP] Sterline Irlandesi
* [ILS] Nuovo Shekel Israeliano
* [ISK] Corona Islandese
* [ITL] Lire Italiane
* [JMD] Dollari Giamaicani
* [KRW] Won Sudcoreano
* [LKR] Rupia di Sri Lanka
* [LTL] Litas Lituano
* [LVL] Lats Lettoni
* [MAD] Dirham Marocchino
* [MMK] Kyat Birmano
* [MXN] Peso Messicano
* [MYR] Ringgit Malese
* [MZN] Metical Mozambicano
* [NIO] Nicaraguan córdoba
* [NLG] Fiorino dei Paesi Bassi
* [NOK] Corone Norvegesi
* [PAB] Balboa Panamense
* [PEN] New Sol Peruviano
* [PHP] Peso Filippino
* [PKR] Rupia Pakistana
* [PLN] Zloty Polacco
* [PTE] Scudi Portoghesi
* [RON] Nuovo Leu Rumeno
* [RSD] Dinaro Serbo
* [RUB] Rubli Russi
* [SEK] Corone Svedesi
* [SGD] Dollaro di Singapore
* [SIT] Tallero Sloveno
* [SKK] Corona della Slovacchia
* [THB] Baht Thailandese
* [TND] Dinaro Tunisino
* [TRL] Lira Turca
* [TWD] Nuovo Dollaro Taiwanese
* [UAH] Hryvnia Ukraina
* [VEB] Bolivar Venezuelano
* [VEF] Bolivar Forte Venezuelano
* [VND] Dong Vietnamita
* [XAF] Franco delle Colonie Francesi Africane
* [XCD] Dollaro dei Caraibi Orientali
* [XPF] Franco delle Colonie Francesi del Pacifico
