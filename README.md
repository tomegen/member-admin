# member-admin

## Anleitung "mitgliederverwaltung" Applikation

**Vorbereitung Linux/Mac-Nutzer:** <br>
sourceCode (python) herunterladen. <br>
Installation von Python 3.12. benötigt + pip <br>
Packages pandas, icalendar, customtkinter, datetime, tkcalendar, tkinter, configparser werden benötigt. <br>
main-Methode in mitgliederverwaltung.py sollte genutzt werden. 

**Vorbereitung Windows-Nutzer:** <br>
"mitgliederverwaltung_VERSION.exe" + config.ini herunterladen<br><br>

**Anleitung zur Nutzung des Tools:** <br>
"README.md" kann genutzt werden als Anleitung und für hilfreiche Tipps. <br>
"Release_Notes.md" zeigt alle Änderungen zwischen den neuen Versionen, die veröffentlicht werden. <br>

Anpassung "config.ini": <br>
Das Tool kann mit Excel-Dateien im ".xls" oder ".xlsx" Format umgehen. <br>
In der ersten Zeile erwartet das Tool eine Beschriftung der jeweiligen Spalte (z.B. Vorname für die Vornamenspalte). <br>
In den darauffolgenden Zeilen werden alle Mitglieder erwartet mit befüllten Daten.<br>
Benötigte Parameter: Vorname, Nachname, Mitgliedsdatum, Geburtstag und der Mitgliederstatus müssen befüllt sein. <br>
Optionale Parameter: Alle anderen Werte sind optional<br><br>

**Konfigurationen:** <br>
birthday.possibilities: Gibt an, welche Geburtstage in der Applikation überhaupt auswählbar sind. <br>
honor.possibilities: Gibt an, welche Ehrungen in der Applikation überhaupt auswählbar sind. <br>
excel_columns: Gibt den Namen der Spalte an, die in der Applikation befüllt sind <br>
Beispiel: Die Vornamen sind in der Spalte A eingetragen. Wähle den Wert des Feldes A1, z.B. "Vorname" und trage ihn unter "first_name" ein.<br><br> 

Nachdem die Konfigurationsdatei komplett befüllt wurde, kann die ".exe" Datei gestartet werden.<br>
Die aktuelle Mitgliederanzahl und neuen Mitglieder im aktuellen Jahr werden als Label dargestellt. <br>
Außerdem gibt es die Möglichkeiten "Geburtstage" und "Ehrungen", die selbsterklärend sind. 

