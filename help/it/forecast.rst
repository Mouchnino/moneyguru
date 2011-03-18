Prevedere il futuro
===================

Alcune transazioni vengono ripetute in maniera regolare, come gli stipendi, le bollette, i noleggi, le rate del mutuo, etc.. Queste sono perfette per le **Pianificazioni**. Altre spese, invece, possono essere stimate, come gli alimentari, l'abbigliamento, il tempo libero, etc.. Questo sono adatte alle **Previsioni**. Con le funzionalità di pianificazione e previsione di moneyGuru è possibile prevedere la propria situazione finanziaria futura.

Come funziona
-------------

Sia le pianificazioni che le previsioni funzionano tramite un sistema di "occorrenze". Quando si crea una pianificazione o una previsione nelle viste che portano proprio questi nomi, in realtà si crea una transazione "madre", dalla quale una serie di occorrenze verrano create a intervalli regolari (specificati nella transazione madre) e verranno poi mostrare nelle viste Transazioni e nelle viste Conto.

Le occorrenze di una pianificazione possono essere modificate direttamente dalle viste Transazioni e Conto; quando lo si fa, moneyGuru chiede l'applicabilità di questa modifica: si può modificare solo la particolare occorrenza (se ad esempio un pagamento ricorrente è stato diverso dal solito), oppure si possono modificare tutte le transazioni future collegate (se ad esempio un noleggio dovesse ad un certo punto aumentare).

Quando si modifica una pianificazione madre, gli effetti si applicano a tutte le occorrenze, **eccetto** quelle che sono state modificate manualmente.

Le occorrenze di una Previsione sono leggermente diverse; esse non possono essere modificate direttamente, ma il loro ammontare è influenzato da altre transazioni. Tutte le transazioni che fanno riferimento al conto destinazione di tipo Uscite o Entrate di una previsione ridurranno l'ammontare dell'occorrenza che copre le date di queste transazioni. Per capire meglio basta un esempio: se si crea una previsione mensile "abbigliamento" di 100 Euro, creando una transazione che trasferisce 20 Euro al conto "abbigliamento" in Luglio, si avrà che l'occorrenza del 31 Luglio calerà da 100 Euro a 80 Euro.

Un'altra caratteristica delle occorrenze delle previsioni è che si trovano esclusivamente *nel futuro*. Nonappena la loro data viene raggiunta, queste scompaiono.

Creare una Pianificazione
-------------------------

Per creare una transazione pianificata, si va nella vista Pianificazione e si fa click sul pulsante "Nuovo Elemento". Il pannello Info Pianificazione comparirà del tutto simile a quello delle transazioni, salvo avere alcuni campi ulteriori: Tipo di Ripetizione, Ripeti Ogni e Data di Fine. Il primo campo determina se la ripetizione deve essere giornaliera, settimanale, etc.. Il secondo stabilisce quanti di questi periodi si vuole che passino da una transazione alla successiva. Per esempio, se si vuole una pianificazione quindicinale (due settimane), si deve impostare Tipo di Ripetizione a "settimanale" e Ripeti Ogni a 2. 

Se si possiede già una "transazione modello" da cui si vuole creare la pianificazione, c'è una scorciatoia nei menu chiamata "Crea Pianificazione dalla selezione". Questo creerà una nuova pianificazione e copierà tutti i dati dalla transazione selezionata.

Quando si crea una transazione pianificata, tutte le occorrenze future di quella pianificazione per l'intervallo di date corrente verranno mostrate; si possono riconoscere dal piccolo |clock| accanto alla voce.


Modifica di una pianificazione
------------------------------

Oltre ad essere possibile farlo attraverso la vista Pianificazione, è anche possibile modificare *una qualsiasi occorrenza* nelle viste Transazione e Conto! Le occorrenze possono essere modificate come una qualsiasi altra transazione, ma esistono alcuni trucchi premendo il tasto Shift:

* **Modifica di una solo occorrenza:** se si modifica una singola voce come una transazione qualsiasi, un'eccezione verrà creata nella pianificazione e solo questa voce conterrà la modifica.
* **Modifica di tutte le occorrenze future:** A volte si può voler modificare una pianificazione da un certo momento in poi. Per farlo basta tenere premuto Shift quando si termina la modifica della transazione. Tutte le occorrenze future verrano adeguate.
* **Saltare un'occorrenza:** Volete pianificare un'astensione non retribuita di 3 settimana dal lavoro? Basta cancellare le opportune voci pianificate del vostro salario, come transazioni qualsiasi.
* **Terminare una pianificazione:** Non tutte le pianificazioni sono infinite. Per terminarla ad una certa data, basta selezionare la prima occorrenza successiva all'ultima che si vuole mantenere, e cancellarla tenendo premuto Shift.

Come si può vedere, il concetto è molto semplice: le pianificazioni possono essere modificate come una qualsiasi transazione, ma se tiene premuto Shift le modifiche verranno applicate a tutte le occorrenze future.

**Quando le occorrenze si concretizzano:** Pianificare le transazioni è semplice, ma ad un certo punto devono concretizzarsi. In moneyGuru "accadono" realmente quando la transazione viene riconciliata. In quel momento l'occorrenza si trasforma in una normale transazione, perdendo il suo |clock| e la possibilità di essere utilizzata per modificare le occorrenze future.


Fare Previsioni
---------------

Una previsione può essere creata dalla vista omonima tramite un pannello molto simile a quello delle pianificazioni. Il campo Conto è l'Entrata o l'Uscita per la quale si fa la previsione (Abbigliamento, Stipendio, etc..). Il campo opzionale Destinazione permette di specificare un'Attività o una Passività da utilizzare come secondo lato della transazione. Quando lo si specifica, la parte "futura" del grafico di bilancio in quel conto rifletterà il cambiamento che ipoteticamente avverrà.

Attenzione però a non dimenticare che impostando un conto Destinazione **non** limita la previsione a solo quel conto. Per esempio, se si crea una previsione di 200 Euro per *Abbigliamento*, con un conto destinazione *Conto Corrente*, comunque anche acquistando 50 Euro di vestiti con la carta di credito (transazione dal conto di passività *Carta di Credito* al conto Uscite *Abbigliamento*) l'occorrenza della previsione rifletterà correttamente quanto previsto per quel mese, scendendo a 150 Euro.

Normalmente il conto più adatto ad essere usato come conto destinazione è il conto corrente principale, dato che è definitiva il posto da cui viene e verso cui va il denaro alla fine. Lo scopo della destinazione di una previsione è solo di riflettersi nei bilanci futuri; quindi  se ad esempio si sceglie come destinazione il conto passività Carta di Credito, a meno che non ci sia una transazione pianificata che regolarmente paga la società della carta, il bilancio futuro di quella carta crescerà indefinitamente.


Integrazione con Cashculator
----------------------------

**Questa caratteristica richiede Cashculator v1.2.2 o successivo.**

Le funzionalità di previsione e pianificazione in moneyGuru sono ottime se si sa già a quali tipi di previsioni ci si vuole limitare. Infatti moneyGuru non consente di giocare con delle Ipotesi, ovvero delle previsioni ipotetiche che hanno lo scopo di progettare la previsione che si andrà ad utilizzare. Esiste un'altra applicazione di un altro sviluppatore che è specializzata in esattamente questo: `Cashculator <http://www.apparentsoft.com/cashculator>`__.

moneyGuru si integra con Cashculator per consentire di esportare facilmente i dati "Reali" (è così che li chiamano) verso Cashculator, progettare le proprie previsioni, e infine reintegrarle in moneyGuru. Per utilizzare questa funzionalità integrata, bisogna seguire i passi:

1. Scaricare Cashculator, eseguirlo una volta (moneyGuru necessita della struttura del database di Cashculator) e chiuderlo.
2. Aprire il proprio documento moneyGuru, aprire una nuova scheda e fare click sul pulsante "Cashculator".
3. La scheda mostrerà una lista dei propri conti Entrate e Uscite. Attraverso questa lista si deve scegliere quali conti sono Ricorrenti e quali Non Ricorrenti (è una differenza importante in Cashculator).
4. Fare click su "Esporta Conti". Questo esporterà tutti i conti Entrate e Uscite, così come il loro flusso di cassa degli ultimi 4 mesi. Non preoccupatevi se avete dei dati originali in Cashculator: moneyGuru crea la sua copia del database di Cashculator e inserisce là i dati.
5. Assicuratevi che Cashculator sia chiuso, quindi fate click su "Avvia Cashculator". Si deve utilizzare questo pulsante per lanciare, poiché moneyGuru gli deve dire di utilizzare il proprio database invece di quello originale.
6. In Cashculator comparirà uno scenario ipotetico chiamato "moneyGuru", che conterrà tutti i conti oltre ai loro dati "Reali" degli ultimi 4 mesi. Si può quindi procedere ad utilizzare questi dati per progettare la propria previsione, o Budget (fare riferimento al manuale di Cashculator per i dettagli).
7. Una volta finito si possono creare le pianificazioni e le previsioni in moneyGuru. Bisognerà farlo manualmente, ma questo è un limite temporanea di questa funzionalità (vedi sotto).
8. Cashculator sarà ripristinato alla sua modalità normale (il suo database) quando si esce da moneyGuru.


**Per il momento, l'integrazione con Cashculator funziona in una sola direzione (esportazione).** Il modo in cui Cashculator funziona è molto diverso da quello di moneyGuru. Esportare i dati non è molto complicato, ma quando si tratta di reimportare le previsioni in moneyGuru le cose si fanno più complicate. Ci sono molti modi in cui si possono riempire le celle "Piano" in Cashculator e non c'è un modo ovvio di convertirli automaticamente in previsioni e pianificazioni.