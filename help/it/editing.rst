Modificare un documento moneyGuru
=================================

I fondamenti
------------

Ci sono alcuni tasti e alcuni click che funzionano allo stesso modo per ogni cosa in moneyGuru. Innanzitutto, c'è un insieme di 3 pulsanti nell'angolo in basso a sinistra:

|edition_buttons|

Il pulsante + crea un qualcosa di nuovo, il pulsante - rimuove un qualcosa di selezionato e il pulsante "i" mostra le informazioni, o proprietà aggiuntive, del qualcosa selezionato. Il "qualcosa" dipende dalla vista corrente. Nello Stato Patrimoniale e nel Conto Economico è un conto. Nelle viste Transazioni e Conto è una transazione. Inoltre se si seleziona più di una transazione e si fa click sul pulsante "i", il pannello di Modifica di Massa verrà mostrato al posto dei dettagli della singola transazione.

Ovviamente è anche possibile fare la stesse cose con la tastiera. |cmd|\ N crea una qualcosa di nuovo, Delete o Indietro rimuovono un qualcosa di selezionato e |cmd|\I mostra le informazioni relative al qualcosa selezionato.

Si può modificare un qualcosa anche facendo doppio click su una cella modificabile (per esempio, la cella nome di un conto). Si può inoltre iniziare a modificare qualcosa selezionandolo e premendo Invio. Si può annullare la modifica premendo Escape, ripristinando la riga al suo contenuto precedente.

Quando si è in modalità di modifica, Tab e Shift-Tab possono essere utilizzati per navigare tra le celle modificabili. Quando non ci sono più celle in una riga la modifica termina. Si può anche terminare la modifica premendo Invio.


I Conti
-------

I conti possono essere modificati dallo Stato Patrimoniale e dal Conto Economico. Quando si crea un nuovo conto, questo verrà creato nel tipo di conto che contiene la selezione attuale. Per esempio, se si ha un conto "Carta di Credito" selezionato e si preme |cmd|\ N, allora una nuova passività verrà creata. Si può quindi inserire un nome e premere Invio per terminare.

Si può anche utilizzare il drag & drop (trascinamento con il mouse) per modificare il tipo o il gruppo di un conto (già, si possono creare dei gruppi di conto con |cmd_shift|\ N).

|edition_account_panel|

Utilizzando Mostra Info su di un conto, si visualizzerà il pannello di modifica nell'immagine precedente. Da qui si possono cambiare il nome del conto, il tipo, la sua :doc:`valuta <currencies>` e il numero di conto. Un numero di conto è solo un riferimento per quel conto, che si può utilizzare per riferirsi al proprio conto corrente o come meglio si crede (per dire, 1000-1999 per le Attività, 8000-8999 per le Uscite, e cose simili). Quando un conto possiede un numero, questo verrà mostrato nelle viste Transazioni e Conto. Per di più p possibile inserire il numero invece del nome per farvi riferimento (se ce lo si ricorda a mente, l'inserimento diventa molto più veloce).

About accounts and currencies: You can only change the currency of an account that has no
:doc:`reconciled entry <reconciliation>`. If for some reason you want to change the currency of such
an account, you'll have to de-reconcile its entries first. Si noti che modificare la valuta di un conto **non** modifica la valuta delle transazioni che contiene.


Transazioni
-----------

Le transazioni sono modificate dalle viste Transazioni e Cono. Quando si crea una nuova transazione, la data della transazione precedentemente selezionata viene inizialmente proposta (vedi "Modifica delle Date" più sotto). Le colonne Descrizione, Beneficiario e Conto (Da, A) sono auto-completate (vedi "Auto-completamento" più sotto). 

Si può riordinare una transazione all'interno di altre transazioni con la stessa data tramite il drag & drop, oppure con |cmd|\ + e |cmd|\ -.

Se si digita il nome di un conto che non esiste nella colonna Conto, questo verrà automaticamente creato come un'Entrata o un'Uscita a seconda dell'ammontare della transazione. Non preoccupativi di errori di battitura che potrebbero creare un sacco di conti che poi tocca andare a cancellare: se si corregge un nome di conto in una transazione che lo ha automaticamente creato, esso verrà altrettanto automaticamente rimosso.

|edition_transaction_panel|

Utilizzando il pannello Mostra Info su una singola transazione fa comparire il pannello qui sopra. In esso è possibile modificare tutto quello che si modifica dalle viste Transazione e Conto, ma in più è possibile creare una transazione con più di due elementi, comunemente chiamata "Transazione Multipla", tramite la tabella in fondo.

Una cosa da ricordarsi a riguardo della modifica di questa tabella è che è costantemente auto-bilanciata. Perciò se si prende una transazione e si prova a cancellare una delle sue voci, questa non sparirà, in quanto verrà automaticamente riaggiunta con un conto non assegnato, di pari ammontare. Modificando l'ammontare di una riga creerà automaticamente una riga non assegnata con un ammontare pari alla differenza. Quindi se si vuole inserire una transazione multipla, come per esempio un compagno di stanza che a fronte di una bolletta di 40 Euro pagata da voi tramite addebito su conto corrente, vi dà 20 Euro in contanti, si deve:

#. Aggiungere una normale transazione da Conto Corrente --> a Bollette.
#. Fare click su Mostra Info per quella transazione.
#. Modificare il debito del conto Bollette a 20 Euro, ottenendo così la creazione di una terza riga non assegnata con 20 Euro di debito.
#. Modificare il conto della terza riga indicando Contanti.

|edition_three_way_split|

Complimenti, avete creato la vostra prima transazione multipla! Questa riflette correttamente la realtà in cui 40 Euro sono usciti dal vostro conto corrente, l'utenza ha avuto un costo netto di 20 Euro e voi vi trovate 20 Euro in contanti in più nel portafoglio.

|edition_mass_edition_panel|

Utilizzando Mostra Info su più di una transazione selezionata fa comparire il pannello qui sopra. Con questo è possibile fare modifiche di massa: quando si preme Salva, tutte le transazioni selezionate avranno i valori marcati dal segno di spunta modificati in base a quanto inserito nel campo accanto.


Modifica delle date
-------------------

Ogni volta che si modifica una data, lo si fa tramite uno speciale componente grafico dotato di tre campi: giorno, mese e anno. Quando si inizia un'operazione di modifica di una data, è sempre il **giorno** ad essere il primo campo selezionato, indipendentemente dal formato della data. Ci si può spostare all'interno dei campi con le frecce sinistra e destra, incrementando un campo con le frecce su e giù. Ovviamente si può anche inserire direttamente tutta la data e il componente cambierà automaticamente campo quando si inserisce il carattere separatore, oppure la lunghezza massima è stata raggiunta. Per chiarire, ecco le regole:

* Il formato di visualizzazione è sempre quello di sistema.
* Il formato di ingresso è sempre giorno --> mese --> anno.
* Indipendentemente dal formato della data, se ne può inserire una senza separatori, a patto di inserire gli zeri dove servono per mantenere le doppie cifre. Per esempio, se il formato di data è mm/dd/yy, si può inserire "07/06/08" digitando "060708".
* Indipendentemente dal formato della data, se ne può inserire una con i separatori. Per esempio, se il formato di data è yyyy-mm-dd, si può inserire "2008-07-06" digitando "6-7-08".
* Si può premere la lettera "T" per inserire al volo la data di oggi.

Mentre si modifica una voce, se si inserisce una data al di fuori dell'intervallo di date correnti, verrà visualizzato un |backward_16| o un |forward_16|. Ciò significa che se l'intervallo è di tipo "navigabile" (Mese, Quarto, Anno), l'intervallo verrà adeguato quando si termina l'inserimento in modo da mantenere visualizzata la transazione inserita. Se l'intervallo di date attuali non è "navigabile" (Anno ad Oggi, Anno Corrente, Personalizzato), la transazione sparirà dalla vista.


Modifica dell'Ammontare
-----------------------

I campi che permettono l'inserimento di una valuta hanno alcune caratteristiche nascoste.
* Si possono inserire semplici espressioni tipo "2+4.35/2", che verranno automaticamente calcolate.
* Se è stato attivata l'opzione "Imposta automaticamente i decimali mentre digito", si otterrà quando descritto. Per esempio, se la valuta attuale è USD, inserendo "1234" risulterà in "12.34".
* Si può sempre specificare la valuta di un ammontare anteponendo o facendolo seguire la codice ISO a 3 cifre (vedi :doc:`valute <currencies>`).


Auto-completamento, Auto-riempimento e Lista di Completamento
-------------------------------------------------------------

moneyGuru ha un sistema di auto-completamento e auto-riempimento molto avanzato. Nonappena si digita qualcosa in un campo auto-completabile (Descrizione, Beneficiario, Conto), moneyGuru esaminerà le altre transazioni per proporre un completamento. Si può passare da un valore proposto all'altro tramite le frecce su e giù, ed accettarla uscendo dal campo con una Tabulazione. Ovviamente si può anche semplicemente proseguire a digitare.

L'auto-riempimento consente di riempire i campi vuoti dopo che si esce con una Tabulazione da un campo auto-completabile. Per esempio, se il Beneficiario è la prima colonna auto-completabile, digitando un beneficiario già esistente farà sì che i campi successivi siano riempiti con i valori dell'ultima transazione relativa a quel beneficiario.

In Mac OS X è possibile ottenere una lista di ricerca per qualsiasi campo auto-completabile. Se devi inserire un beneficiario che sai **di sicuro** di avere in una qualche transazione, ma di cui non ricordi come inizia, basta premere |cmd|\ L e una finestra di ricerca comparirà, elencando tutti i beneficiari. Il campo di ricerca permette di effettuare una ricerca fuzzy (ovvero non serve sapere le prime lettere, ma solo alcune lettere) che evidenzierà all'inizio della lista i beneficiari più rilevanti.

.. |edition_buttons| image:: image/edition_buttons.png
.. |edition_account_panel| image:: image/edition_account_panel.png
.. |edition_transaction_panel| image:: image/edition_transaction_panel.png
.. |edition_three_way_split| image:: image/edition_three_way_split.png
.. |edition_mass_edition_panel| image:: image/edition_mass_edition_panel.png
.. |backward_16| image:: image/backward_16.png
.. |forward_16| image:: image/forward_16.png
