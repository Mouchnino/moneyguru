Mit moneyGuru können Sie Dateien in den Formaten QIF, OFX, QFX sowie CSV importieren. Wählen Sie dazu "Importieren..." aus dem "Ablage" Menü und selektieren die Datei, die Sie importieren möchten. Es öffnet sich der Importdialog:

![](images/import_window.png)

Sollten in der zu importierenden Datei mehr als ein Konto vorhanden sein, so erscheint für jedes Konto ein eigener Tab. In jedem Tab werden die Daten aus der Datei entsprechend angezeigt. Vor jeder Zeile haben Sie mit einem Kontrollkästchen die Möglichkeit zu entscheiden, ob diese Zeile übernommen werden soll oder nicht. Nachdem Sie alle Zeilen kontrolliert haben und diejenigen, die nicht importiert werden sollen, abgewählt haben, klicken Sie auf "Import". Nur das ausgewählte Konto wird dann in moneyGuru übernommen.

Probleme mit dem Datumsformat
-----

Beim Import einer Datei versucht moneyGuru automatisch das richtige Datumsformat zu erkennen. Dabei werden alle Zeilen analysiert und ein Format gewählt, das auf alle Daten passt. Allerdings kann es vorkommen, dass es nicht möglich ist, das richtige Datumsformat mit Gewissheit zu bestimmen; beispielsweise lässt "01/02/03" die Bestimmung der Position für Tag/Monat/Jahr nicht zu. moneyGuru wählt dann intern ein mögliches gültiges Datumsformat, das jedoch mit Hilfe der "Tausch" Schaltfläche umgestellt werden kann. Sollte beispielsweise moneyGuru "dd/mm/yy" als Datumsformat gewählt haben, in der zu importierenden Datei befinden sich aber Daten im Format "mm/dd/yy", so wählen Sie "Tag <--> Monat" und klicken "Tausch". Es ist möglich, die Datumsformatierung für alle Konten (Tabs) dieses Imports mit Hilfe von "Auf alle Konten anwenden" durchzuführen.

Vertauschen von Beschreibung und Empfänger
-----

Sollten die Felder "Beschreibung" und "Empfänger" aus unerfindlichen Gründen vertauscht sein, so können Sie im Dropdown-Feld "Beschreibung <--> Empfänger" auswählen und "Tausch" klicken.

Import in bereits bestehendes Konto
-----

Im Normalfall werden Transaktionen bei einem Importvorgang in ein neues Konto importiert. Es ist jedoch auch möglich, die Transaktionen in ein bestehendes Konto einzufügen, sofern Sie ein gültiges Zielkonto auswählen. Im Fall des Importes einer OFX Datei wird, falls vorhanden, das Zielkonto automatisch ausgewählt. Beim Importvorgang in ein bereits bestehendes Konto ändert sich der Dialog ein wenig und sieht dann so aus:

![](images/import_match_table.png)

Es ist ja nun möglich, dass in der zu importierenden Datei Transaktionen existieren, die bereits in moneyGuru erfasst wurden, daher ist es dem Benutzer möglich, Zeile für Zeile zu prüfen, ob diese importiert werden soll. Im Fall des Importes einer OFX Datei wird pro Transaktion automatisch überprüft, ob diese zu importieren ist, jedoch kann hier der Benutzer ebenfalls im Bedarfsfall eingreifen.

Auf der linken Seite der Tabelle (die ersten 3 Spalten) befinden sich die [nicht wertgestellten](reconciliation.htm) Transaktionen des Zielkontos. Auf der rechten Seite sieht man alle zu importierenden Transaktionen. Befindet sich eine Transaktion nur in der zu importierenden Datei oder dem Zielkonto, so ist die entsprechende Seite mit den Daten gefüllt, die andere Seite ist leer. Ist eine zu importierende Transaktion bereits in moneyGuru vorhanden, so ist diese auf beiden Seiten vorhanden, und Schloss Symbol wird in der Mitte angezeigt. Diese "Verbindung" der gleichen Transaktion kann durch Klick auf das Schloss Symbol aufgebrochen werden. Mittels Drag & Drop können zwei nicht gleichartige, nicht verbundene Transaktionen in Verbindung gebracht werden.

Im Fall des Importes einer OFX Datei in ein Zielkonto, in das bereits früher eine OFX Datei importiert wurde, werden alle oben beschriebenen Verbindungen automatisch gesetzt. Hier gibt es auch eine Ausnahme zur Regel, dass links nur nicht wertgestellte Transaktionen angezeigt werden: Sollte eine Transaktion aus der zu importierenden OFX Datei bereits als wertgestellte Transaktion in moneyGuru existieren, so wird diese Transaktion ebenfalls angezeigt, das "Import" Kontrollkästchen wird dann jedoch deaktiviert (ist im Normalfall aktiviert). Hier wird angenommen, dass eine bereits wertgestellte Transaktion nicht durch einen Import überschrieben werden soll.

Import von CSV Dateien
-----

Das Importieren von CSV Dateien erfolgt prinzipiell gleich wie der Import von anderen unterstützten Dateien, allerdings mit einem Zwischenschritt. Der Benutzer muss moneyGuru zuerst mitteilen, was in welcher Spalte der CSV Datei zu finden ist:

![](images/import_csv_options.png)

Das CSV Format ist ein völlig offenes Format zum Austausch beliebiger Daten, es gibt keine festgeschriebene Struktur, welches Feld an welcher Stelle zu stehen hat. Mit diesem Dialog kann moneyGuru mitgeteilt werden, wo sich was befindet. Zuerst sollten Sie mit Hilfe der in der Tabelle dargestellten Datei herausfinden, was in den einzelnen Spalten angezeigt wird (beispielsweise das Transaktionsdatum). Sobald dies feststeht, können Sie durch Klick in den Spaltenkopf den Feldtyp auswählen. Hierbei ist zu beachten, dass die Angabe von "Datum" und "Betrag" verpflichtend sind.

In CSV Dateien finden sich oftmals Kopfzeilen (manchmal sogar Fußzeilen), die jedoch keine zu importierenden Transaktionen beinhalten. moneyGuru kann nicht automatisch herausfinden, ob es sich um eine solche Zeile ohne Daten handelt, daher müssen Sie hierbei das entsprechende "Import" Kontrollkästchen deaktivieren.

In seltenen Fällen kann es vorkommen, dass moneyGuru beim Import der Datei nicht erkennt, mit welchen Zeichen die Spalten getrennt sind. Dies resultiert in einer Darstellung von offensichtlich komplett wirren Daten, teils über mehrere Spalten hinweg. Sollten Sie so etwas beobachten, können Sie mit Hilfe des "Spaltentrenner" Feldes festlegen, welches Zeichen in dieser Datei zur Spaltentrennung verwendet wird. Haben Sie das richtige Zeichen eingegeben, können Sie "Neu einlesen" anwählen, um die Datei mit dem korrekten Spaltentrenner einzulesen.

moneyGuru merkt sich die Zuordnung der Felder zu den Spalten sowie die Position der Kopf- und Fußzeilen, auch über einen Neustart hinweg. Sollten Sie mehr als eine CSV Dateivariante importieren wollen, können Sie die Layout Funktionalität nützen. Jedes Layout speichert die Konfiguration der Felder beziehungsweise der Kopf- und Fußzeilen.

Weiters ist es möglich, das Zielkonto gleich hier mit anzugeben. Das gewählte Zielkonto wird in den eigentlichen Importdialog mit übernommen, sollten Sie jedoch die Konfiguration in einem Layout speichern, so wird hier das Zielkonto ebenfalls mit dem Layout mitgespeichert.
