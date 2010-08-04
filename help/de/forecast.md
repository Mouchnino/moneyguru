Ein Teil Ihrer Transaktionen wird immer wiederkehrend sein, wie zum Beispiel die Gehaltszahlung, das Abbuchen der Mietkosten, Kreditrückzahlungen, oder ähnliches. Ein anderer Teil der Transaktionen wird vohersehbare Grenzen nicht überschreiten, wie zum Beispiel Ausgaben für Lebensmittel, Kleidung oder Ausgehen. Mit der Hilfe der Funktionalität von **Wiederholungen** und **Budgets** können Sie einen Überblick über Ihre Finanzsituation auch in der Zukunft gewinnen.

Wie es funktioniert
-----

Sowohl Wiederholungen wie auch Budgets arbeiten mit "Ereignissen". Wenn Sie eine Wiederholung oder ein Budget (in der entsprechenden Ansicht beziehungsweise dem entsprechenden Tab), so wird eine "Haupttransaktion" erzeugt. Ausgehend von dieser Haupttransaktion werden regelmässig Ereignisse generiert und in den Ansichten für Transaktionen sowie einzelnen Konten hinzugefügt.

Ereignisse, die durch eine Wiederholung erzeugt wurden, können direkt in der Ansicht "Transaktionen" sowie eines Kontos editiert werden. Sollten Sie etwas geändert haben, so fragt moneyGuru nach, ob Sie nur dieses eine Ereignis oder dieses sowie alle folgenden Ereignisse ändern wollen. Beispielsweise ändern Sie das Ereignis nur einmal (Bonuszahlung zum Lohn), oder für alle Folgeereignisse (Erhöhung des Lohns).

Wenn Sie eine Haupttransaktion einer Wiederholung ändern, so betrifft dies alle Ereignisse, die von dieser Wiederholung erzeugt wurde, *außer* Ereignisse, die Sie händisch editiert haben.

Budgetereignisse verhalten sich hier anders. Diese können nicht editiert werden, der Betrag wird aber durch andere Transaktionen beeinflusst. Alle Transaktionen, die ein Ein- beziehungsweise Ausgabekonto, auf das ein Budget eingerichtet wurde, betreffen, verringern den Betrag des Budgets. Sollten Sie planen, monatlich 100 EUR für Kleidung auszugeben, so würde eine Transaktion mit 20 EUR auf "Kleidung" das Budget (das als Transaktion am Monatsletzten angezeigt wird) um 20 EUR auf 80 EUR verringern.

Eine weitere Besonderheit von Budgetereignissen ist, dass diese immer "in der Zukunft" liegen. Sollte das Datum des Budgetereignis erreicht werden, "verschwindet" das Ereignis.

Anlegen einer Wiederholung
-----

Um eine Wiederholung zu erzeugen, wechseln Sie in den Tab "Wiederholungen" und klicken auf "Neuer Eintrag". Ein Dialogfenster, das ähnlich aussieht wie die Transaktionsdetails, wird angezeigt. Sie finden hier zusätzlich Felder für die Konfiguration der Ereignisintervalle. Sie können hier festlegen, ob die Ereignisse jeden dritten Montag im Monat, wöchentlich oder alle zwei Monate erzeugt werden sollen, und ob die Ereignisserie auch an einem gewissen Tag endet.

Sie können auch aus einer bestehenden Transaktion (zum Beispiel die Zahlung der Mietkosten auf Ihrem Bankkonto) eine Wiederholung erzeugen. Dazu wählen Sie aus dem Menü "ausgewählte Transaktion wiederholen".

Ereignisse, die aus einer Wiederholung erzeugt wurden, werden mit dem kleinen Symbol ![](images/clock.png) dargestellt, um erkenntlich zu machen, dass es sich um eine Wiederholung handelt.

Widerholungsereignis editieren
-----

Zusätzlich zur Möglichkeit, die Wiederholung im entsprechenden Tab zu editieren, können Sie auch jedes Ereignis einer Wiederholung editieren:

* **Nur ein Ereignis ändern:** Ändern Sie ein Ereignis wie eine normale Transaktion, damit bleibt nur das editierte Ereignis modifiziert, alle anderen Ereignisse sind davon nicht betroffen.
* **Alle zukünftigen Ereignisse ändern:** Wenn Sie beim Beenden der Änderung des Ereignis die Umschalttaste gedrückt halten, so wird das aktuelle sowie auch alle zukünftigen Ereignisse geändert.
* **Ereignis auslassen:** Soll das Taschengeld für eine Woche nicht ausbezahlt werden? Löschen Sie das Ereignis einfach wie eine normale Transaktion.
* **Wiederholung beenden:** Möchten Sie die Wiederholung beenden, so wählen Sie einfach das Ereignis der Serie, das auf das letzte geplante Ereignis folgt, und halten beim Löschen die Umschalttaste gedrückt. Nun werden diese sowie alle zukünftigen Ereignisse gelöscht.

Das Drücken der Umschalttaste beim Abschluss von Änderungen eines Ereignisses betrifft also die geänderte sowie alle zukünftigen Ereignisse.

**Ereigniseintritt:** geplante Ereignisse werden in normale Transaktionen überführt, wenn sie mittels dem Wertstellungsmodus wertgestellt werden (damit wird auch das Symbol ![](images/clock.png) entfernt). Ab diesem Zeitpunkt kann diese Transaktion nicht mehr herangezogen werden, um etwaige Änderungen an zukünftigen Ereignissen vorzunehmen.

Budgetierung
-----

Budgets können im entsprechenden Tab erstellt werden. Die Konfiguration der Intervalle ist analog zur Konfiguration von Intervallen bei Wiederholungen. Das Feld "Konto" beinhaltet das Ein- beziehungsweise Ausgabekonto, für das das Budget erstellt werden soll (Kleidung, Ausgehen, ...). Im Feld "Zielkonto" kann ein Konto aus den Aktiva oder Passiva eingetragen werden, das die andere Seite der Transaktion darstellt. Ist hier ein Konto ausgewählt, so wird das Budget nur in der Kontoansicht des entsprechenden Kontos angezeigt.

Die Auswahl eines Zielkontos beeinflusst jedoch nicht die Funktionsweise des Budgets bei Transaktionen mit anderen Zielkonten. Wenn Sie ein 200 EUR Budget für das Ausgabekonto "Kleidung" mit Ihrem Girokonto anlegen, und mit der Kreditkarte um 50 EUR Kleidung kaufen, so wird trotzdem korrekterweise vom 200 EUR Budget der Betrag von 50 EUR abgezogen, das Budget wird somit auf 150 EUR verringert.

Das Konto, das sich am besten für ein Zielkonto eignet, ist üblicherweise das "Hauptkonto", dort laufen alle Finanzein- und -ausgänge zusammen. Die richtige Konfiguration erlaubt eine bessere Berechnung der zukünftigen Gesamtsalden.

Cashculator Integration
-----

**This feature requires Cashculator v1.2.2 or later.**

The budgeting and scheduling features in moneyGuru are good if you already know what kind of budgets you want to stick to. However, moneyGuru doesn't let you play around with hypothetical budgets in order to design the budget you're going to adopt. There's a nice app from another developer that specializes in that: [Cashculator](http://www.apparentsoft.com/cashculator).

moneyGuru integrates with Cashculator to make it easy for you to export "Actual" (that's what they call it) data to Cashculator, design your budgets, and then add those budgets back to moneyGuru. To use this integration feature, follow these steps:

1. Download Cashculator, run it once (moneyGuru needs Cashculator's skeleton of its database) and close it.
2. Open your moneyGuru document, open a new tab and click on the "Cashculator" button.
3. The tab will show a list of your income and expense accounts. Through this list, you have to choose which of your accounts are Recurring and which and Non-Recurring (it's an important distinction in Cashculator).
4. Click on "Export Accounts". This will export all your income and expense accounts as well as their cash flow for the last 4 months. Don't worry about your regular Cashculator data. moneyGuru makes its own copy of Cashculator's database and exports its data there.
5. Make sure that Cashculator is closed, then click on "Launch Cashculator" which will launch Cashculator. You need to use this button to launch it because it tells Cashculator to use moneyGuru's database instead of its own.
6. In Cashculator, there's going to be a scenario called "moneyGuru" which contains all your accounts as well as their "Actual" data for the last 4 months. Use this data to design yourself a budget (please refer to Cashculator's documentation for that)
7. Once you're done, you can create budgets and schedules according to your design in moneyGuru. You'll have to do it manually, but that's a temporary limitation of the feature (see below).

**For now, the Cashculator integration only works one way (export).** The way Cashculator works is very different from the way moneyGuru works. Exporting data isn't so complicated, but when comes the time to import back budgets in moneyGuru, things get a little trickier. There're lots of ways you can fill "Plan" cells out in Cashculator and there's no obvious ways to automatically convert that into budgets and schedules.

This feature is brand new (introduced in v2.1) and what I'd like to do is to test the waters a little bit. If you use this feature, please let me know how you use Cashculator and how you think your data should look like back in moneyGuru. Please, use the [support forums](http://getsatisfaction.com/hardcodedsoftware) for that. Thanks!
