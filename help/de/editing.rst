Editieren einer moneyGuru Datei
===============================

Grundlagen
----------

Ein paar Tastenkürzel beziehungsweise ein paar Schaltflächen bedeuten in moneyGuru immer das gleiche. Zuallererst befinden sich in der linken unteren Ecke des Anwendungsfensters folgende drei Schaltflächen:

|edition_buttons|

Die Schaltfläche mit dem Plus erzeugt ein neues Element, die mit dem Minus löscht das ausgewählte Element, das "i" bringt einen Dialog mit Details zum ausgewählten Element. Das "Element" ist abhängig von der Art des aktuell angezeigten Tabs. Im Eigenkapital beziehungsweise in Profit & Verlust handelt es sich hierbei um Konten, in der Transaktionsansicht sowie in der Kontoansicht handelt es sich um Transaktionen. Werden mehr als eine Transaktion ausgewählt und die Schaltfläche mit dem "i" gedrückt, so wird der Massenänderungsdialog angezeigt.

Natürlich gibt es auch Tastenkürzel für diese Aktionen: |cmd|\ N erzeugt ein neues Element, die Löschtaste entfernt das ausgewählte Element, und |cmd|\ I bringt den Dialog mit Details zum ausgewählten Element.

Es ist möglich, mit einem Doppelklick auf eine editierbare Zelle (beispielsweise der Kontoname) in den Änderungsmodus zu wechseln. Dies gilt auch für die Auswahl eines Elements und dem Drücken der Entertaste. Dabei wird das erste editierbare Feld ausgewählt.

Im Änderungsmodus wird die Tabulatortaste für die Vorwärts-Navigation zwischen editierbaren Feldern verwendet (mit gedrückter Umschalttaste und Tabulatortaste wird rückwärts navigiert). Gibt es kein weiteres editierbares Feld mehr, so endet der Änderungsmodus - dies gilt auch für das Drücken der Entertaste. Mittels der Escape-Taste können Sie eine Änderung abbrechen und damit alle Änderungen rückgängig machen.

Konten
------

Konten können in den Ansichten "Eigenkapital" und "Profit & Verlust" editiert werden. Wenn Sie ein neues Konto anlegen, so wird es automatisch unter der Kontoart des aktuell ausgewählten Kontos angelegt. Haben Sie beispielsweise Ihr Kreditkartenkonto ausgewählt und drücken |cmd|\ N, so wird das neue Konto unter der Sparte "Passiva" erzeugt. Geben Sie dann den Namen des Kontos ein und drücken die Entertaste um das Erzeugen abzuschließen.

Sie können mit Drag & Drop unter der falschen Gruppe angelegte Konten verschieben und damit korrigieren. Sie können unter "Profit & Verlust" auch Kontogruppen verschieben (eine neue Kontogruppe erzeugen Sie mit |cmd_shift|\ N).

|edition_account_panel|

Wenn Sie "Details anzeigen" wählen, so wird der oben angezeigte Dialog angezeigt. Sie können hier den Namen des Kontos, die Kontoart, die zugeordnete :doc:`Währung <currencies>` wie auch eine Kontonummer ändern. Die Kontonummer dient zur besseren Anzeige in den Transaktions- sowie Kontoansichten; Sie können auch beim Erfassen von Transaktionen die Nummer anstatt des Kontonamens eintippen. Dies dient einfach der Flexibilität und unterstützt Sie bei Ihrer Finanzverwaltung, falls Sie bisher das Arbeiten mit Kontonummern gewöhnt sind.

Achtung: Sollten Sie die Währung eines Kontos ändern, so werden dadurch nicht automatisch auch die Währung jeder Transaktion dieses Kontos geändert!

Transaktionen
-------------

Transaktionen können Sie in der Ansicht "Transaktionen" sowie den Kontoansichten ändern. Erzeugen Sie eine neue Transaktion, so wird automatisch das Datum der zuvor ausgewählten Transaktion mit übernommen (siehe auch "Ändern eines Datums" weiter unten). Des weiteren wird für die Felder "Beschreibung", "Empfänger sowie "Konto" (Debit- wie auch Kreditkonto) automatisch vervollständigt (Siehe "Autovervollständigung").

Die Reihenfolge von Transaktionen mit dem gleichen Datum lässt sich mit Drag & Drop verändern, Sie können für das gleiche Vorhaben auch |cmd|\ + und |cmd|\ - benützen. 

Wenn Sie bei der Eingabe eines Debit- oder Kreditkontos einen Namen eintippen, den es bisher noch nicht gibt, so wird dieser automatisch als neues Ein- beziehungsweise Ausgabekonto erzeugt (abhängig von der Transaktion). Sie brauchen jetzt aber nicht zu fürchten, dass Tippfehler zu einer Unzahl an sinnlosen neu angelegten Konten führt, denn sobald Sie Ihren Tippfehler editieren, wird das Konto, falls dies die einzige relevante Transaktion ist, wieder gelöscht.

|edition_transaction_panel|

Mit "Details anzeigen" wird der oben dargestellte Dialog angezeigt. Hier ist es möglich, alle Felder, die auch in den Transaktions- wie auch Kontoansichten änderbar sind, zu editieren. Zusätzlich ist es mit der Tabelle im unteren Bereich des Dialogs auch möglich, die Transaktion aufzusplitten, das heisst, Teilbeträge auf unterschiedliche Konten zu verbuchen.

Aufgrund der notwendigen Einhaltung der doppelten Buchhaltung führt jede Änderung von Teiltransaktionen immer dazu, dass die Gesamttransaktion weiterhin ausgeglichen bleibt. Sollten Sie eine Teiltransaktion löschen, so verschwindet der "fehlende Geldbetrag" nicht einfach, sondern er wird automatisch auf ein Konto namens "Nicht zugeordnet" verbucht. Kaufen Sie beispielsweise in einem Supermarkt um 40 EUR ein, haben dabei aber um 20 EUR einen Pullover erstanden, den Sie statt auf "Lebensmittel" natürlich lieber auf das Ausgabekonto "Kleidung" buchen möchten, so gehen Sie wie folgt vor:

#. Erzeugen Sie eine "normale" Transaktion über 40 EUR mit von Ihrem Bargeldkonto auf "Lebensmittel"
#. In der Detailansicht, ändern Sie in der Tabelle den Debitbetrag auf 20 EUR. Damit wird eine zusätzliche Teiltransaktion mit 20 EUR erzeugt.
#. Sie können nun das Zielkonto der neuen Teiltransaktion auf "Kleidung ändern"

|edition_three_way_split|

Das angezeigte Beispiel zeigt eine andere, auf ähnlich erzeugte Weise erzeugte aufgesplittete Transaktion.

|edition_mass_edition_panel|

Wenn Sie mehr als eine Transaktion ausgewählt haben und "Details anzeigen" drücken, wird der Massenänderungsdialog wie oben dargstellt angezeigt. Sobald Sie "Speichern" drücken, wird jedes Feld aller ausgewählten Transaktionen auf den eingegeben Wert gesetzt, sofern Sie das zugehörige Kontrollkästchen aktiviert haben.

Ändern eines Datums
-------------------

Ein Datum besteht aus den Komponenten Tag, Monat und Jahr. Sobald Sie in den Editiermodus gelangen und ein Datumsfeld wird angewählt, so ist als erstes immer die Komponente "Tag" ausgewählt, in welcher Form auch immer das Datumsformat eingestellt ist. Mit Hilfe der Pfeiltasten links und rechts gelangen Sie zu den anderen Komponenten, und mit Hilfe der Pfeiltasten oben und unten können Sie den angezeigten Wert inkrementieren beziehungsweise dekrementieren. Natürlich können Sie das Datum auch mit den Zifferntasten händisch eingeben. Sobald beim Eingeben des Tages mit Zifferntasten die Maximallänge einer Komponente erreicht ist, wird die nächste Komponente aktiviert, und Sie befinden sich beim Monat. Die folgenden Regeln gelten also:

* Das Datumsformat wird aus den Systemeinstellungen übernommen.
* Das Eingabeformat folgt immer der Reihenfolge Tag --> Monat --> Jahr.
* Unabhängig der Konfiguration des Datumsformates können Sie immer die Variante mit führenden Nullen eingeben. Wenn Ihr Datumsformat nach der Form "dd.mm.yy" konfiguriert ist, so können Sie die Eingabe des 7. Juni 2008 mit der Ziffernfolge "070608" erzielen.
* Einen Wechsel zwischen Komponenten erzielen Sie auch mit der Eingabe des Trenners. Sollte Ihr Datumsformat nach der Form "yyyy-mm-dd" konfiguriert sein, so können Sie die Eingabe des 7. Juni 2008 auch mit der Tastenfolge "7-6-08" erzielen.
* You can press the letter "T" to quickly set the date to today.

Sollten Sie beim Eingeben eines Datums Werte eingeben, die ausserhalb des aktuell ausgewählten Zeitraums liegen, bekommen Sie ein Symbol der Form |backward_16| oder |forward_16| angezeigt. Sobald der Änderungsmodus beendet ist, wird der ausgewählte Zeitraum auf einen Zeitraum gesetzt, in dem die soeben modifizierte Transaktion liegt, und die Transaktion wird angezeigt. Dies gilt jedoch nur für "navigierbare" Zeiträume (Monat, Quartal, Jahr). Im Fall von nicht navigierbaren Zeiträumen (laufendes Jahr, benutzerdefiniert, ...) "verschwindet" die Transaktion vom aktuell dargestellten Zeitraum (bleibt jedoch selbstverständlich gespeichert).

Ändern von Beträgen
-------------------

Es gibt in den Betragsfeldern einige versteckte Funktionen:

* Sie können innerhalb von Betragsfeldern einfache "Formeln" berechnen, wie zum Beispiel "2+4,35/2".
* Mit der Einstellung "Dezimalstellen automatisch setzen" ist es nicht notwendig, das Dezimalkomma zu verwenden. Sollte beispielsweise in Ihrer Systemeinstellung die Währung EUR konfiguriert sein, so führt die Eingabe von "1234" automatisch zum Betrag "12,34" Euro.
* Sie können immer die Währung eines Betrages durch Vor- beziehungsweise Nachstellung des dreibuchstabigen ISO Währungscodes angeben (siehe auch Hilfeseite zu :doc:`Währungen <currencies>`).

Autovervollständigung, Autoausfüllen
------------------------------------

In moneyGuru gibt es Funktionen zur Autovervollständigung beziehungsweise zu Autoausfüllen von Werten. Sobald Sie sich in einem Feld befinden, für das die Autovervollständigung gilt (Beschreibung, Empfänger, Konto), wird moneyGuru alle anderen Transaktionen evaluieren und Ihnen während Sie Tastatureingaben machen die nächstbeste Vervollständigung vorschlagen. Mit Hilfe der Pfeiltasten (oben und unten) können Sie durch die Vorschläge navigieren, sollten mehrere Möglichkeiten zur Auswahl stehen. Möchten Sie die Vervollständigung übernehmen, so verwenden Sie die Tabulatortaste. Natürlich können Sie auch einfach weitertippen, ohne die Vervollständigungen zu verwenden.

Es gibt auch Felder, die die Funktion "Autoausfüllen" auslösen, wie zum Beispiel "Empfänger". Sobald Sie hier einen Wert eingeben, für den bereits andere Transaktionen existieren, wird moneyGuru Ihnen die restlichen Felder automatisch mit den Belegungen der letzten Transaktion füllen.

In der Mac OS X Version können Sie auch die Funktion "Kandidatenlisten" nützen. Sollten Sie sich in einem Feld (beispielsweise "Empfänger") befinden, und wissen nicht genau, wie genau Sie den gewünschten Empfänger bei der letzten Transaktion eingegeben haben, so geben Sie einfach einen Wortteil ein, von dem Sie wissen, dass er auf alle Fälle vorkommt. Sollten Sie dann |cmd|\ L drücken, erscheint eine Kandidatenliste mit allen Möglichkeiten, die den eingegebenen Wortteil enthalten.
