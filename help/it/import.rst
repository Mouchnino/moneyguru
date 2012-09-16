Importare i dati in moneyGuru
=============================

moneyGuru supporta l'importazione dai formati QIF, OFX, QFX e CSV. Per importare un file, si utilizza la voce "Importa.." del menu "File" per poi selezionare un file. Facendolo, la finestra di importazione apparirà così:

|import_window|

Per ogni conto presente nel file da importare, verrà creata una scheda nella finestra di importazione. Questa finestra di dialogo è abbastanza intuitiva da usare. La colonna più a sinistra con una casella di selezione stabilisce quali transazioni importare. Basta esaminare le transazioni che si vogliono importare, deselezionare quelle che non si vuole e poi fare click per importale. Solo il conto selezionato viene importato.

Correggere le date
------------------

moneyGuru determina automaticamente il formato delle date di un file importato, guardando tutte le date e scegliendo solo un formato che abbia senso per tutte quante. Comunque, a volte un file importato può avere delle date ambigue (come "01/02/03"), quindi moneyGuru non può esser sicuro della scelta. In questi casi, moneyGuru prenderà il primo formato adattabile, ma se non dovesse essere quello giusto, basta usare il pulsante Scambia. Per esempio, se moneyGuru avesse scelto dd/mm/yy ma il file contenesse in effetti mm/dd/yy, basta scegliere "Giorno <--> Mese" nella casella in alto a destra e premere Scambia. Si può applicare lo scambio a tutti i conti nella finestra di importazione, scegliendo "Applica a tutti i conti" prima dello scambio.

Scambiare descrizione e beneficiario
------------------------------------

In alcuni casi, i campi descrizione e beneficiario sono scambiati. Potrebbe essere un errore dell'applicazione che ha creato il file, o un'ambiguità nel formato del file, o qualsiasi cosa. Non importa, perché lo si può correggere nella finestra di importazione selezionando "Descrizione <--> Beneficiario" nel selettore dello scambio, e poi premendo "Scambia". Problema risolto. 

.. todo:: Update the 2 section below with the new "Fix broken fields" section.

Importare in un conto esistente
-------------------------------

Di norma le transazioni vengono importate in un conto nuovo. Tuttavia, è possibile importarle in un conto esistente cambiando il conto destinazione. Importando un file OFX, il conto destinazione è automaticamente selezionato, se ha senso. Se si seleziona un conto destinazione, la corrispondente tabella cambia leggermente diventando:

|import_match_table|

La ragione per cui la tabella cambia a quel modo è perché se si importa in un conto esistente, è possibile trovarsi ad importare transazioni che esistono già nel conto. Bisogna dire a moneyGuru quale transazione va con quale. Se si importa un file OFX, tutto ciò viene fatto automaticamente, ma lo si può comunque modificare manualmente se si vuole.

Sul lato sinistro della tabella (prime 3 colonne) ci sono le transazioni :doc:`Non Riconciliate <reconciliation>` del conto destinazione. Sulla destra ci sono le transazioni da importare. Le transazioni che non si sovrappongono hanno uno dei due lati liberi. Al contrario, le transazioni che si sovrappongono hanno entrambi i lati e l'icona di un lucchetto nel mezzo. Si possono separare le transazioni facendo click sul lucchetto e riunirle trascinandole una sull'altra.

Se si importa un file OFX in un conto in cui era già stato importato un file OFX, tutto questo avviene automaticamente. Ciò porta ad un'eccezione alla regola che solo transazioni non riconciliate sono presenti sul lato di sinistra. Se una transazione nel file OFX importato combina con una transazione riconciliata dal conto destinazione, questa transazione si vedrà lì. Comunque, la casella "importa" sarà automaticamente deselezionata (di solito invece è selezionata). La ragione è che se è riconciliata, probabilmente non la si vuole cambiare.

Importazione da CSV
-------------------

Importare i file CSV è come importare un qualsiasi altro tipo di file, ma prima di arrivare alla finestra principale di importazione, si deve dire a moneyGuru quale colonna CSV è cosa.

|import_csv_options|

Il problema con i CSV è che non c'è assolutamente alcuno standard su come deve essere strutturato il file. Questa finestra permette di dirlo a moneyGuru. Per usarla basta guardare i dati mostrati e, una volta capito quale colonna contiene cosa (ad esempio la data), fare click sull'intestazione della colonna e selezionare l'opportuno campo della transazione. Le colonne Data e Ammontare sono obbligatorie. 

I file CSV hanno spesso delle righe di intestazione (e a volte anche di chiusura in fondo). moneyGuru non ha idea inizialmente di che cosa rappresentino le righe, perciò a responsabilità dell'utente deselezionare ogni riga che non rappresenta una transazione.

A volte i file CSV sono così strani che moneyGuru non riesce a capire correttamente quale sia il delimitatore che separa un campo dall'altro. Se accadesse, si avrebbero i dati più assurdi nelle varie colonne, con mezzo dato in una colonna e mezzo nell'altro. In quei casi, si può utilizzare il campo **Delimitatore** per specificare manualmente il carattere. Dopodiché è sufficiente premere Rianalizza per ricaricare le colonne tramite il nuovo separatore.

moneyGuru si ricorda delle colonne e delle intestazioni da una sessione di esecuzione e l'altra, perciò se si hanno più tipi di file CSV da importare frequentemente, si possono utilizzare diverse Disposizioni, ognuna delle quali memorizza la propria configurazione di colonne e intestazioni.

Si può anche specificare un conto destinazione direttamente nella finestra delle opzioni CSV. Si ottiene lo stesso risultato specificandolo in seguito, nella finestra di importazione, eccetto per il fatto che se lo si specifica qui, verrà memorizzato nella Disposizione.