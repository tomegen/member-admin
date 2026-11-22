
# Version 0.2.1
Release Date: 22.11.2026 <br/><br>

Import: Unbekannte Geburtstage, Eintrittsdaten und Austrittsdaten blockieren die Übernahme nicht mehr. Sie bleiben
leer (im Assistenten orange markiert) und stehen danach in der Datenprüfung, bis sie ergänzt sind. Neue Mitglieder
und neue Austritte in der App brauchen die Daten weiterhin. <br>
Import: Mehr Vornamen werden beim Schätzen des Geschlechts erkannt (z. B. Xaver, Kilian, Leonie, Marleen). <br><br>

# Version 0.2.0
Release Date: 22.11.2026 <br/><br>

**Die Excel-Datei wird zur gemeinsamen Mitgliederdatenbank.** Sie bleibt in Excel, Google Tabellen und am Handy
bearbeitbar und kann in Dropbox, OneDrive/SharePoint, Google Drive oder Nextcloud geteilt werden. <br>
Neu: Standardformat mit Blättern Mitglieder, Funktionen, Einstellungen, Änderungsprotokoll und Info
(Auswahllisten, Datumsprüfung, Mitgliedsnummer, Geschlecht, Status aktiv/passiv/ausgetreten, Austritt, E-Mail,
Abteilung, Beitragsklasse, Bemerkung). <br>
Neu: Tab „Mitglieder“ – anlegen, bearbeiten, Austritt erfassen, Funktionen/Ämter, Nummern vergeben. <br>
Neu: Sicheres Speichern – Sicherung vor jedem Speichern (Ordner „Sicherungen“), Änderungen anderer bleiben erhalten,
Rückfrage nur bei gleichzeitig geändertem Feld, Schutz bei in Excel geöffneter Datei, Änderungsprotokoll. <br>
Neu: Import-Assistent für bestehende Listen (xlsx, xls, csv): Spalten- und Wertevorschläge, „Name, Vorname“ und
„PLZ Ort“ trennen, fehlende Angaben für viele Zeilen auf einmal ergänzen, Geschlecht aus dem Vornamen schätzen. <br>
Neu: Liste abgleichen (z. B. Verbandsexport, E-Mail-Liste) und Konfliktkopien der Cloud-Dienste zusammenführen. <br>
Neu: Einstellungen des Vereins in der Datei: Anlässe mit Geschenk (erscheint in Vorschau und Exporten),
Auswahllisten, Vereinsname, Erinnerung, ob passive Mitglieder zählen, Löschfrist. <br>
Neu: Löschfrist für Ausgetretene mit Hinweis und Löschen nach Bestätigung (Protokoll wird anonymisiert). <br>
Neu: Die geöffnete Datei wird überwacht und bei Änderungen von außen neu eingelesen. <br>
Geändert: Listen in einem anderen Format werden nicht mehr direkt ausgewertet, sondern einmalig übernommen; die
bisherige Liste bleibt unverändert. Die in 0.1 gewählten Geburtstage/Jubiläen gehen in die neue Datei über. <br><br>

# Version 0.1.0
Release Date: 17.11.2026 <br/><br>

Neue Oberfläche (Qt statt Tk), läuft als Windows-EXE und als Mac-App. <br>
Neu: Download-Seite (tomegen.github.io/member-admin), Windows-Installer (ohne Administratorrechte, mit Desktop-Symbol) und Mac-Disk-Image (in „Programme“ ziehen). <br>
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
