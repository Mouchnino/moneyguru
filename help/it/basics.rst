Elementi di base di moneyGuru
=============================

moneyGuru è sostanzialmente basato sul sistema a `partita doppia`_. L'elemento centrale del sistema è la **transazione**, che rappresenta un movimento di denaro da uno (o più) conti ad un altro (o più) conti in una particolare data. Una transazione consiste in un insieme di 2 o più voci a somma nulla tra 2 o più conti. Qualsiasi conto, sia che sia un'Attività che un'Entrata può trasferire denaro a qualsiasi altro conto. Ciò risulta pratico quando si deve :doc:`gestire il contante <cash>`. Non c'è molto altro da dire di fondamentale sul sistema in sé. Le cose diventano appena più complicate quando sono coinvolte più valute, ma i relativi dettagli sono descritti nella :doc:`pagina relativa alle valute <currencies>`.

Schede e viste
--------------

moneyGuru è organizzato in diverse viste (le principali sono illustrate più sotto) attraverso le quali si gestisce il documento di moneyGuru. Queste viste sono a loro volta gestite attraverso delle schede. Le schede si comportano come quelle di qualsiasi altra applicazione analoga. Si apre una nuova scheda con |cmd|\ T, la si chiude con |cmd|\ W e ci si sposta dall'una all'altra con |cmd_shift|\ ←→. Ogni volta che si apre un conto con la freccia |basics_show_account_arrow|, una nuova scheda viene aperta (o se era già aperta viene attivata) con quel conto.

L'intervallo di date
--------------------

L'intervallo di date correntemente selezionato si riflette sull'intera applicazione. Tutto ciò che si vede nelle viste è relativo a quell'intervallo di date. Per esempio, se "Gen 2010 - Dic 2010" è selezionato, tutto ciò che si vede in qualsiasi vista ha una data compresa tra il 01/01/2010 e il 31/12/2010. L'intervallo di date è controllato da questo piccolo componente:

|basics_date_range|

Ci sono 7 tipi di intervallo di date:

#. **Mese:** Inizia il primo giorno del mese e termina l'ultimo giorno del mese.
#. **Quarto:** Inizia il primo giorno del quarto (3 mesi) e termina l'ultimo giorno del quarto.
#. **Anno:** Inizia il primo giorno di quell'anno e termina l'ultimo giorno dello stesso anno.
#. **Anno ad oggi:** Inizia il primo giorno dell'anno di *oggi* e termina *oggi*. Si utilizza questo intervallo per far sì che moneyGuru mostri la situazione attuale (senza alcuna previsione o pianificazione) futura.
#. **Anno corrente:** Questo intervallo di date *segue* la data odierna. Mostra cioè esattamente *un anno*, ma invece di mostrare anni interi, sfrutta l'impostazione "Mesi successivi nell'anno corrente" per determinare quando l'intervallo finisce; dopodiché fa iniziare l'intervallo esattamente un anno prima.
#. **Tutte le transazioni:** Questo intervallo inizia dalla data della più vecchia transazione nel documento e finisce alla data odierna + i mesi successivi descritti prima.
#. **Intervallo personalizzato:** Quando si seleziona questo intervallo, moneyGuru chiederà una data di inizio e una data di fine, quindi le utilizzerà come intervallo.

Per gli intervalli "mobili" (Mese, Quarto, Anno), si possono utilizzare le frecce per selezionare il precedente o il successivo (sulla tastiera con |cmd_opt|\ [ e |cmd_opt|\ ]). C'è anche una scorciatoia per selezionare i tipi di intervallo  (|cmd_opt|\ 1-7). Si può anche premere |cmd_opt|\ T per ritornare all'intervallo oggi.

Quando si selezionano degli intervalli personalizzati, è possibile far salvare a moneyGuru tale intervallo in una di 3 posizioni disponibili. Facendolo, un nuovo intervallo apparirà nel menu e sarà selezionabile rapidamente.


La sottile linea rossa
----------------------

Tutte le informazioni in moneyGuru sono mostrate coerentemente con l'intervallo di date selezionato. Le cose si fanno interessanti quando un intervallo di date termina nel futuro. Se avete delle pianificazioni o delle previsioni impostate, i numeri che vedrete e i grafici le includeranno. Nei grafici, c'è una netta distinzione tra passato e futuro. Il passato è disegnato in verde, mentre il futuro in grigio: una sottile linea rossa li separa. Quindi, quando si guarda alla parte grigia del grafico, si vede qualcosa che ancora non è avvenuto. Il Patrimonio Netto nella scheda Stato Patrimoniale terrà conto di queste transazioni ancore non avvenute, così come delle previsioni. A volte, interessa solamente sapere lo stato attuale della propria situazione finanziaria: questo è ciò a cui serve l'intervallo "Anno ad oggi" (|cmd_opt|\ 4).

.. todo:: Add "Visibility Options" section

Patrimonio Netto e Guadagni & Perdite
-------------------------------------

|basics_net_worth|

Le viste Patrimonio Netto e Guadagni & Perdite sono quelle che consento di gestire i propri conti e di esaminare statistiche relative alla propria situazione finanziari. Entrambe hanno un'impostazione simile e si comportano allo stesso modo.

**Stato Patrimoniale e Conto Economico:** In alto a sinistra c'è lo "Stato Patrimoniale" (per il Patrimonio Netto) o il "Conto Economico" (per Guadagni e Perdite), ovvero un foglio che elenca i conti, mostra i totali e i gruppi di conti. I totali sono sempre forniti nella propria valuta di sistema. Si può anche :doc:`aggiungere, modificare e rimuovere <editing>` i conti da questo foglio.

**Mostra Conto:** Accanto a ciascun conto, c'è una piccola |basics_show_account_arrow|. Facendovi click sopra viene mostrato in conto nella vista Conto. Si può anche selezionare premendo |cmd|\→.

**Escludi Conto:** Si può anche "escludere" alcuni conti facendo click sull'iconcina |basics_account_out|, oppure premendo |cmd_shift|\ X. I conti esclusi non sono considerati nei totali o nei grafici del foglio.

**Grafico a Torta:** Sulla destra del foglio di ogni vista, ci sono due grafici a torta che mostrano il peso di ciascun conto di ogni tipo. Se ci sono dei gruppi di conti, è possibile raggrupparli nella visualizzazione del foglio, per vedere anche i loro valori raggruppati nel grafico. Per esempio, se c'è un gruppo "Automobile" contenente alcuni conti, è possibile raggrupparli per avere un'unica fetta intitolata "Automobile" (invece che avere una fetta per Carburante, una per Assicurazione, etc..).

**Grafico:** Il grafico in basso mostra la progressione della statistica principale (patrimonio netto o guadagno netto) nel tempo.

**Colonne:** I fogli hanno ognuno un diverso insieme di colonne (personalizzabile con |cmd|\ J).

* **Stato Patrimoniale (vista Patrimonio Netto):**

    * **Conto #:** Un numero di conto opzionale, legato al conto. Vedi :doc:`pagina di modifica <editing>` per maggiori dettagli.
    * **Inizio:** Il saldo del conto all'inizio del periodo. Include le Pianificazioni, ma non le Previsioni.
    * **Fine:** Il saldo del conto alla fine del periodo.
    * **Variazione:** La differenza tra Inizio e Fine.
    * **Variazione %:** La differenza tra Inizio e Fine in percentuale.
    * **Previsto:** L'ammontare di una Previsione (di cui questo conto è la destinazione) che rimane da allocare nell'intervallo di date corrente. Ciò significa che, se le Previsioni riflettono correttamente la realtà, il valore di Fine + quello di Previsto dovrebbe corrispondere al saldo effettivo alla fine del periodo.
    
* **Conto Economico (vista Guadagno & Perdita):**

    * **Conto #:** Come nel foglio dello Stato Patrimoniale.
    * **Attuale:** Il flusso di denaro del conto fino a questo momento.
    * **Ultimo:** Il flusso di denaro del conto per l'intervallo precedente. Per esempio, se si sta visualizzando un intervallo Mese, la colonna Ultimo si riferisce al mese precedente. L'intervallo Anno ad Oggi è un caso speciale, in cui viene visualizzato quello dell'anno precedente.
    * **Variazione e Variazione %:** Come nel foglio Stato Patrimoniale.
    * **Previsto:** L'ammontare di una Previsione che rimane da allocare a questo conto nell'intervallo di date. Ciò significa che se le previsioni riflettono la realtà correttamente, allora Attuale + Previsto dovrebbe corrispondere al movimento di denaro netto effettivo alla fine dell'intervallo.


Transazioni
-----------

|basics_transactions|

Nella vista Transazioni, sono elencate tutte le transazioni del documento per l'intervallo di date selezionato. Da qui è possibile :doc:`aggiungere, modificare e rimuovere <editing>` una transazione. Questa vista è la più pratica per aggiungere un insieme di transazioni (se si hanno ad esempio una pila di scontrini e ricevute). **Ammontare** è il valore che viene trasferito. **Da** e **A** contengono il nome dei conti a cui si riferisce la transazione (se è una transazione multipla, i nomi sono separati da virgole). In pratica queste colonne significano "Questa Transazione trasferisce **Ammontare** dal conto **Da** al conto **A**". Per esempio, se **Da** è "Conto Corrente" e **A** è "Alimentari", del denaro è stato tolto dal Conto Corrente e messo in "Alimentari". Per un'entrata **Da** potrebbe essere "Stipendio" e **A** invece "Conto Corrente". 

Sopra alla lista di transazioni, c'è una **barra filtri** che permette di vedere solo certi tipi di transazioni.

* **Entrate:** Mostra solo le transazioni che includono almeno un conto Entrata.
* **Uscite:** Mostra solo le transazioni che includono almeno un conto Uscita.
* **Trasferimenti:** Mostra solo le transazioni che si riferiscono solo ad Attività e Passività.
* **Non Assegnato:** Mostra solo le transazioni che hanno un conto non assegnato.
* **Riconciliato:** Mostra solo le transazioni aventi almeno una voce riconciliata.
* **Non Riconciliato:** Mostra solo le transazioni non aventi voci riconciliate.

Le celle **Da** e **A** hanno una piccola |basics_show_account_arrow| alla loro destra. Analogamente ai fogli Stato Patrimoniale e Conto Economico, è possibile farvi click sopra per mostrare il conto. Se una transazione è multipla e quindi riporta più di un conto nella casella, solo il primo verrà aperto.

.. todo:: Add "Modification Time" paragraph

Conto
-----

|basics_account|

Questa vista mostra le transazioni *dal punto di vista di un particolare conto*. Si può aprire la vista Conto facendo click sulle |basics_show_account_arrow| nelle altre viste. Questa vista elenca le transazioni in maniera simile alla vista Transazioni, ma limitandosi a quelle afferenti il Conto visualizzato. Al posto delle colonne **Da** e **A**, c'è solo la colonna **Trasferimento**, ovvero *l'altro lato(i)* della transazione. Analogamente, la colonna **Ammontare** è divisa in una colonna **Incremento** e una **Decremento**. Per esempio, se sto visualizzando il Conto Corrente e il **Trasferimento** è "Alimentari" e il **Decremento* è "42", questo significa che 42$ (o Euro, o altra valuta) sono stati trasferiti dal Conto Corrente al conto Alimentari. Se il conto visualizzato è un'Attività o una Passività, c'è anche una colonna **Saldo**, che mostra il saldo corrente del conto. Il grafico sottostante mostra il saldo del conto per ogni giorno dell'intervallo di date selezionato. Se il conto mostrato è un'entrata o un'uscita, verrà mostrato un grafico a barre simile a quello della vista Guadagno & Perdita.

La vista Conto ha anch'essa una barra filtro, che si comporta in maniera analoga a quella nella vista Transazioni, salvo alcune differenze.

* **Incremento:** Mostra solo le voci che hanno un ammontare dal lato "Incremento".
* **Decremento:** Mostra solo le voci che hanno un ammontare dal lato "Decremento".
* **Trasferimento:** Mostra solo le voci che hanno si riferiscono solo ad Attività e Passività.
* **Non Assegnato:** Mostra solo le voci non assegnate.
* **Riconciliato:** Mostra solo le voci riconciliate.
* **Non Riconciliato:** Mostra solo le voci non riconciliate.

Il pulsante *Riconciliazione* nella barra filtro (abilitato solo per Attività e Passività) permette di passare la modalità :doc:`Riconciliazione <reconciliation>` da attività a disattivata e viceversa.

Le celle **Trasferimento** hanno una piccola |basics_show_account_arrow| alla loro destra. Analogamente alle altre viste, facendoci click sopra viene aperto il conto mostrato nella cella. A differenza della vista Transazioni però, qui facendoci click sopra più volte nel caso di transazioni multiple, vengono aperti e visualizzati a rotazioni tutti i Conti coinvolti.

A seconda dell'intervallo di date selezionato, ci potrebbe essere una voce **Saldo Precedente** all'inizio della tabella. Questa voce riporta il saldo all'inizio del periodo, come negli estratti conti bancari.

Libro Mastro
------------

Questa vista mette tutti i conti insieme e ne mostra le voci per l'intervallo di date corrente. Il modo in cui vengono presentate le voci è sostanzialmente lo stesso della vista Conto. Questa vista serve per lo più per la creazione di rapporti.


Filtraggio
----------

.. todo:: Update from english version

Il campo Filtro nella barra dei pulsanti permette di vedere tutte le transazioni che corrispondono al testo inserito. Per usarlo, è sufficiente digitare qualcosa e premere invio. Solo le transazioni che hanno una corrispondenza nei campi Descrizione, Beneficiario, Conto #, Conto o Ammontare verranno visualizzate. Se si vogliono vedere le transazioni per alcuni conti o gruppi specifici, digitare "account: conto1,conto2" oppure "group: gruppo1,gruppo2". Questo è molto utile per la :doc:`modifica di massa <editing>`.

Ciò che vedi, è ciò che stampi (circa)
--------------------------------------

In moneyGuru è possibile stampare qualsiasi cosa sia mostrata in una delle quattro viste. Vuoi un rapporto che elenca le transazioni dell'anno scorso? Basta selezionare l'intervallo di date, andare nella vista Transazioni, e premere |cmd|\ P. moneyGuru ridimensiona automaticamente le colonne in base al loro contenuto, provando a riempire il più possibile la pagina.

.. _partita doppia: http://en.wikipedia.org/wiki/Double-entry_bookkeeping_system
.. |basics_show_account_arrow| image:: image/basics_show_account_arrow.png
.. |basics_account_out| image:: image/basics_account_out.png
.. |basics_date_range| image:: image/basics_date_range.png
.. |basics_net_worth| image:: image/basics_net_worth.png
.. |basics_transactions| image:: image/basics_transactions.png
.. |basics_account| image:: image/basics_account.png
