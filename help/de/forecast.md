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

Finanzplanung
-----

Wiederholungen und Budgets erlauben eine bessere Finanzplanung. Man sieht dadurch besser, wie sich die Finanzen vorraussichtlich in der Zukunft entwickeln, des weiteren kann man auch einplanen, wann grössere Anschaffungen wirklich Sinn machen. Planen Sie eine teure Urlaubsreise um 6000 Euro? In der jeweiligen Grafik lässt sich genau der Zeitpunkt bestimmen, ab wann diese Summe verfügbar wird. Wollen Sie sich einen schicken Sportwagen leisten? Die Finanzplanung erlaubt die Entscheidung, ob Neukauf oder doch Leasing die richtige Variante für Sie ist. Natürlich gilt: je besser die Einrichtung der Budgets und Wiederholungen, desto besser die Vorschau auf die zukünftige Finanzsituation.

Die Möglichkeiten zur Finanzplanung sind noch lange nicht ausgereift. Hier wird laufend an zusätzlichen Möglichkeiten gearbeitet.
