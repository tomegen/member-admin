
# Version 0.1.0
Stand: 14.11.2026 (noch nicht veröffentlicht) <br/><br>

Neue Oberfläche (Qt statt Tk), läuft als Windows-EXE und als Mac-App. <br>
Auswertungsjahr wählbar, Vorschau der Ergebnisse vor dem Speichern. <br>
Neu: Export als Excel-Datei, Kalenderdatei (ICS) mit Ganztagsterminen. <br>
Neu: Datenprüfung mit Excel-Zeilennummern statt vieler Warnfenster; prüft auch Alter, Eintritt vor Geburt und doppelte Einträge. <br>
Neu: Übersicht „Demnächst“ (nächste 30 Tage), Tab „Statistik“ (Altersgruppen, Durchschnittsalter, Excel-Export). <br>
Neu: Einstellungen im Programm (Auswahl der Geburtstage/Jubiläen); `config.ini` ist optional. <br>
Neu: Spalten werden an der Überschrift erkannt („Nachname“, „Geburtsdatum“, „Eintritt“ …). <br>
Neu: Leere Excel-Vorlage mit Auswahlfeld und Datumsprüfung (Startseite). <br>
Neu: Kalenderdatei auch für Ehrungen, mit Erinnerung (z. B. 7 Tage vorher). <br>
Neu: „Nur Name und Anlass“ für datensparsame Text-/Excel-Dateien. <br>
Neu: Excel-Datei per Drag & Drop, „Neu einlesen“, zuletzt benutzte Datei merken. <br><br>

Fehlerbehebungen: <br>
- Kalenderexport stürzte ab bei Geburtstagen am 29. Februar (z. B. 2027 für Jahrgang 1952 und 1932). <br>
- Datumsangaben als reine Zahl in Excel wurden stillschweigend als 01.01.1970 gelesen. <br>
- Fehlende optionale Spalten führten zum Absturz, leere Zellen bei „Mitglied“ ebenfalls. <br>
- `config.ini` wurde nur im Arbeitsverzeichnis gesucht. <br>
- Textdateien: Umlaute und doppelte Zeilenumbrüche unter Windows. <br>
- Mitgliederdaten wurden in die Konsole geschrieben. <br>
- „Neue Mitglieder“ zählte immer das laufende Jahr. <br>

# Versionen 0.0.4 – 0.0.7
Interne Korrekturen an der Windows-Build-Pipeline, keine Änderung am Programm. <br>

# Version 0.0.3
Release Date: 01.10.2024 <br/><br>

Bug Fix für Windows .exe Datei: Es war nicht möglich das "customtkinter" Modul einzubinden.<br>
Icon für Desktop-Symbol hinzugefügt. <br>
Beispiels-Excel-Datei hinzugefügt für neue Mitgliederlisten. <br>


# Version 0.0.2
Release Date: 17.09.2024 <br/><br>

Verbesserung des User Interfaces. <br>
Verbesserung der Struktur innerhalb des Codes. <br>
Verbesserung der Validierungen und Fehleranzeigen. <br>

# Version 0.0.1
Release Date: 16.09.2024 <br/><br>

Ermöglichen der Grundfunktionalität dieser Desktop-Applikation.<br/>
Datei mit Konfigurationen kann genutzt werden. <br/>
Geburtstage können als "txt"-Datei generiert werden. <br/>
Geburtstage können als "ics"-Datei generiert werden. <br/>
Ehrungen können als "txt"-Datei generiert werden. <br/>
