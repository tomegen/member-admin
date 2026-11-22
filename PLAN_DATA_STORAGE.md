# Plan: Excel als gemeinsamer Datenspeicher (Standardformat, Pflege in der App, Import)

Stand 2026-11-19, abgestimmt mit Thomas. Noch nichts umgesetzt. Ersetzt die Ideen 31–36 und 45 in `IDEAS.md`
(Idee 39 „Ehrungs-Historie“ entfällt, siehe Entscheidungen).

## Ziel

Die App bleibt lokal installiert, die Daten liegen weiter in **einer Excel-Datei**, die der Verein über Dropbox,
OneDrive/SharePoint, Google Drive, Nextcloud oder USB teilt und die auch ohne App (z. B. am Smartphone) bearbeitet
werden kann. Neu: Die App **pflegt** die Mitglieder selbst (anlegen, bearbeiten, Austritt, löschen), arbeitet nur noch
in **einem festen Standardformat** und bringt einen **flexiblen Import** für bestehende Listen mit. Je besser der
Import, desto mehr Vereine steigen um, deshalb hat er hohe Priorität.

## Entscheidungen (2026-11-19)

| Thema | Entscheidung |
|---|---|
| Schreiben | App pflegt voll (anlegen, bearbeiten, Austritt, löschen). Hebt die Festlegung „App liest nur, schreibt nie“ auf. |
| Aufbau | **Ein** Blatt „Mitglieder“ (eine Zeile pro Person, alle Felder), Zusatzblätter nur für 1:n-Daten und Konfiguration. Kein Haupt-/Detailblatt-Split. |
| Ablage | Alle Varianten müssen funktionieren: Dropbox, Google Drive, OneDrive/SharePoint, Nextcloud, lokal/USB. |
| Parallelität | Selten, 1–3 Pflegende. Keine Sperren, sondern optimistisch mit Prüfung pro Zeile. |
| Speichern | Jede Änderung einzeln: Datei frisch einlesen, betroffene Zeile per Mitgliedsnummer prüfen, nur dann schreiben, sonst Konflikt zeigen. Fremde Änderungen bleiben erhalten. |
| Sicherungen | Ordner `Sicherungen/` neben der Datei (wird mit geteilt). |
| Status | Dropdown aktiv / passiv / ausgetreten, dazu „Austritt am“ und „Austrittsgrund“. |
| Mitgliedsnummer | Vergibt die App. Von Hand ergänzte Zeilen dürfen ohne Nummer sein, die App bietet „Nummern jetzt vergeben?“ an. |
| Altlisten | App arbeitet nur noch im Standardformat. Fremde Listen gehen über den Import-Assistenten (Umwandeln). |
| Import | Variable Spalten, CSV, Werte zuordnen, kombinierte Spalten trennen, fehlende Pflichtangaben im Import nachtragen, Abgleich in eine bestehende Standarddatei. |
| Pflichtfelder | Name, Vorname, Geschlecht, Geburtstag, Eintritt, Status. Alles andere optional. |
| Zusatzfelder | E-Mail, Geschlecht (Anrede wird abgeleitet), Abteilung (ein Wert), Beitragsklasse, Bemerkung. |
| Zusatzblätter | „Funktionen“ (Ämter), „Änderungsprotokoll“, „Einstellungen“ (pro Verein in der Datei, Standardwerte wenn leer), „Info“. **Keine Ehrungs-Historie**: Ehrungen lassen sich für jedes Jahr neu berechnen. |
| Geschlecht im Import | Anrede-Spalte, sonst Vorname (eingebaute Liste), sonst Mehrheit im Verein; geschätzte Werte in der Vorschau markiert und gezählt. |
| Löschen | Austritt behält die Zeile. Einstellung „Löschfrist“: nach X Jahren oder nie. Bei Fälligkeit Hinweis mit Liste und Bestätigung, **nie automatisch**. |
| Konfliktkopien | Beim Öffnen erkennen und zusammenführen (gleicher Abgleich wie beim Import). |
| Auslieferung | Ein großes Release (Vorschlag 0.2.0). |
| Passive Mitglieder | Pro Verein einstellbar, ob sie bei Geburtstagen, Ehrungen und in der Statistik zählen (Standard: ja; Statistik weist aktiv/passiv getrennt aus). |
| Vornamenliste | Klein anfangen (selbst zusammengestellt, häufige Vornamen), mit der Zeit ergänzen. |
| Änderungsprotokoll | Vorerst unbegrenzt. |
| Eintritt unbekannt | ~~Bleibt Pflicht; im Import per Sammel-Ausfüllen nachtragen.~~ **Geändert 2026-11-22 (Test mit echter Liste):** Geburtstag, Eintritt und Austrittsdatum dürfen beim Import leer bleiben (orange, nicht blockierend) und erscheinen in der Datenprüfung; neue Mitglieder/Austritte in der App brauchen sie weiter. Ohne Austrittsdatum greift die Löschfrist nicht. |

## 1. Dateiformat (Schema-Version 1)

Grundsätze für Leute, die die Datei von Hand pflegen: Überschriften fett in Zeile 1, Pflichtspalten blau, Dropdowns
und Datumsprüfung bis Zeile 1001 (die Selbstreparatur erweitert bei Bedarf), fixierte Kopfzeile und Namensspalten, **keine Formeln** in Daten, die die App liest,
kein Blattschutz (Google Tabellen und Excel mobil gehen damit unterschiedlich um), keine Excel-„Tabellen“-Objekte
(gehen beim Speichern aus Google Tabellen verloren).

### Blatt „Mitglieder“ (immer das erste Blatt)

| Spalte | Pflicht | Eingabe | Hinweis |
|---|---|---|---|
| Nr | (App) | ganze Zahl | stabile ID; leer erlaubt, die App vergibt sie |
| Name, Vorname | ja | Text | |
| Geschlecht | ja | Dropdown männlich / weiblich / divers | Anrede (Herr/Frau/–) wird abgeleitet |
| Geburtstag, Eintritt | ja | Datum | bisherige Datumsregeln (Seriennummer, ISO, deutsch) |
| Status | ja | Dropdown aktiv / passiv / ausgetreten | |
| Austritt am, Austrittsgrund | | Datum, Text | |
| Abteilung, Beitragsklasse | | Dropdown aus „Einstellungen“ | ein Wert je Mitglied |
| Straße, PLZ, Ort, Telefon, Mobil, E-Mail | | Text | PLZ als Text (führende Null) |
| IBAN, Mandatsreferenz | | Text | weiterhin keine IBAN-Prüfung |
| Bemerkung | | Text | Kommentar an der Überschrift: keine sensiblen Daten (Gesundheit o. Ä.) |

Fixiert bis Spalte D (Nr, Name, Vorname bleiben beim Wischen am Handy sichtbar). Die App liest und schreibt
**über die Überschrift**, nicht über die Position: Spalten umsortieren geht, zusätzliche eigene Spalten des Vereins
bleiben unangetastet erhalten. Fehlt eine Pflichtspalte (z. B. umbenannt), meldet die App das beim Öffnen mit den
gefundenen Überschriften (wie heute).

### Blatt „Funktionen“

`Nr | Mitglied | Funktion | von | bis | Bemerkung`. „Funktion“ als Dropdown aus „Einstellungen“. Maßgeblich ist die
Nr. „Mitglied“ (Name, Vorname) schreibt die App zur Lesbarkeit als Text dazu. Bei Handeinträgen ohne Nr ordnet die
App über einen eindeutigen Namen zu, sonst Hinweis in der Datenprüfung.

### Blatt „Einstellungen“ (pro Verein, ersetzt QSettings für Vereinsdaten)

Mehrere kleine Listen nebeneinander, jede mit fester Überschrift in Zeile 1, die nach unten wächst (am Handy:
in die nächste leere Zelle tippen):

| Spalten | Inhalt |
|---|---|
| A–D | **Anlässe**: Anlass (Dropdown Geburtstag/Jubiläum) · Jahre · Geschenk/Maßnahme · Bemerkung. Eine Zeile = wird gefeiert. |
| F | Abteilungen |
| G | Beitragsklassen |
| H | Funktionen |
| J–K | **Allgemein** (Einstellung · Wert): Vereinsname, Löschfrist in Jahren (leer/„nie“ = nie), Erinnerung (Tage vorher, ICS), Passive zählen bei Geburtstagen / bei Ehrungen / in der Statistik (je ja/nein, Standard ja) |

Fehlt ein Anlass-Typ ganz, gelten die Standardwerte aus `config.ini` bzw. `DEFAULTS` (wie heute). Ausdrücklich
keine Geburtstage feiern = eine Zeile „Geburtstag | keine“. Die Dropdowns im Blatt „Mitglieder“ verweisen über
**definierte Namen** (`Abteilungen`, `Beitragsklassen`, `Funktionen`) auf diese Spalten. Grund: Direkte Verweise
auf andere Blätter speichert Excel in einer Erweiterung (`extLst`), die openpyxl verwirft. Auf jedem PC bleiben in
`QSettings` nur: zuletzt verwendete Dateien, Name der bearbeitenden Person, Fenstergröße, Auswertungsjahr.

### Blatt „Änderungsprotokoll“

`Zeitpunkt | Bearbeiter | Nr | Mitglied | Aktion | Feld | alt | neu`. Aktionen: angelegt, geändert, Austritt,
gelöscht, Import, zusammengeführt, Nummer vergeben, Einstellungen. Nur Änderungen **über die App** (Handeinträge sind
nicht erfassbar, steht so in „Info“). IBAN im Protokoll maskiert (`DE** … 1234`). Den Namen der bearbeitenden Person
fragt die App einmal pro PC ab (vorbelegt mit dem Benutzernamen).

### Blatt „Info“

Kurzanleitung für die Pflege von Hand, Schema-Version, **Datei-ID** (UUID, erkennt Kopien und Konfliktkopien
unabhängig vom Dateinamen), nächste freie Nr (Formel nur für Menschen, die App liest sie nicht). Löscht jemand das
Blatt, erkennt die App das Standardformat an den Überschriften im Blatt „Mitglieder“ und legt „Info“ beim nächsten
Speichern neu an.

### Selbstreparatur

Bei jedem Schreiben stellt die App fehlende Dropdowns, Datumsprüfungen, Formate, definierte Namen und fehlende
Blätter wieder her. Excel mobil, Google Tabellen und LibreOffice werfen davon gelegentlich etwas weg.

## 2. Sicheres Speichern

Jede Aktion in der App (Mitglied speichern, Austritt, Einstellungen ändern, Nummern vergeben, Import-Abgleich,
Löschen) ist **eine Transaktion**:

1. **Beim Laden** merkt sich die App einen Schnappschuss: Hash der Datei sowie je Nr die normalisierten Zeilenwerte.
2. **Vorprüfung:** Liegt im Ordner `~$<Datei>.xlsx`, ist die Datei auf diesem PC in Excel geöffnet. Hinweis mit dem
   Namen aus der Sperrdatei: „Datei ist in Excel geöffnet (von …). Bitte schließen und erneut speichern.“ Die
   Eingaben im Dialog bleiben erhalten.
3. **Frisch einlesen.** Ist der Hash unverändert, wird direkt geschrieben. Andernfalls wird die betroffene Zeile per
   Nr mit dem Schnappschuss verglichen (**Abgleich je Feld mit drei Ständen**):
   - Feld nur von mir geändert: übernehmen.
   - Feld nur von anderen geändert: deren Wert behalten.
   - Feld von beiden geändert: **Konfliktdialog** „Ihr Wert / Wert in der Datei“.
   - Nr nicht mehr vorhanden: Konfliktdialog (gelöscht oder umnummeriert).
   - Neues Mitglied: Dublettenprüfung (Name + Geburtstag) gegen den frischen Stand, Nr = höchste Nr + 1.
4. **Sicherung:** aktuelle Datei nach `Sicherungen/<Name> JJJJ-MM-TT HHMMSS.xlsx` kopieren. Aufbewahrt werden die
   letzten 30 sowie die jeweils erste je Monat für 12 Monate.
5. **Atomar schreiben:** Arbeitsmappe ändern (nur betroffene Zellen und Protokollzeilen), als
   `~$member-admin-<uuid>.tmp` im selben Ordner speichern, dann `os.replace`. Der Präfix `~$` wird von Dropbox,
   OneDrive und Nextcloud nicht synchronisiert. Unter Windows schlägt `replace` fehl, solange die Datei offen ist
   (`PermissionError`): dann Hinweis, temporäre Datei entfernen, Eingaben bleiben im Dialog.
6. **Nachprüfen:** geschriebene Datei neu einlesen, Änderung kontrollieren, Schnappschuss und Anzeige aktualisieren
   (auch mit Änderungen anderer).

Dazu: `QFileSystemWatcher` auf die Datei. Ändert sie sich von außen (Sync, Excel), zeigt die App „Datei wurde
geändert – neu geladen“ und lädt neu, sofern kein Dialog offen ist.

**Grenze des Verfahrens:** Ist eine Änderung vom Handy noch nicht synchronisiert, schreibt die App auf einen älteren
Stand, und der Sync-Dienst legt eine Konfliktkopie an. Das lässt sich bei Dateisync nicht verhindern, deshalb gibt es
Abschnitt 3.

## 3. Konfliktkopien

Beim Öffnen und nach dem Neu-Laden sucht die App im Ordner (ohne `Sicherungen/`) nach `.xlsx`-Dateien mit
**derselben Datei-ID** im Blatt „Info“. Zusätzlich ein Hinweis an den bekannten Namensmustern (Dropbox
„Konfliktkopie/conflicted copy“, OneDrive „<Name>-<PC-Name>“, Nextcloud „conflicted copy“, Google „(1)“).
Gefunden: Hinweis „Konfliktkopie gefunden: 2 Mitglieder unterscheiden sich“, dann **Zusammenführen-Dialog**
(gleiche Oberfläche wie der Abgleich-Import, Abschnitt 4). Danach landet die Kopie in `Sicherungen/`.

## 4. Import-Assistent (QWizard)

Start über die Startseite („Bestehende Liste importieren“). Das Öffnen einer Datei, die nicht im Standardformat ist,
führt automatisch hierher. Das Original wird nie verändert.

1. **Datei:** `.xlsx`, `.xls`, `.csv`. Bei mehreren Blättern Auswahl. Die **Kopfzeile wird gesucht** (die Zeile unter
   den ersten 10 mit den meisten bekannten Überschriften, für Listen mit Titelzeilen). CSV: Trennzeichen
   (`;` `,` Tab) und Kodierung (UTF-8 mit/ohne BOM, Windows-1252) erkennen.
2. **Spalten zuordnen:** Tabelle „Spalte in Ihrer Datei | Beispielwerte | wird zu …“ (Dropdown). Vorbelegt aus der
   Überschrift (`detect_columns`, erweitert um die neuen Felder) und dem Inhalt (Datum, `@`, IBAN-Muster,
   5-stellige PLZ). **Kombinierte Spalten** mit Vorschau: „Müller, Hans“/„Hans Müller“ → Name/Vorname,
   „12345 Ort“ → PLZ/Ort. Nicht zugeordnete Spalten: ignorieren oder in „Bemerkung“ übernehmen. Die Zuordnung
   wird pro Überschriften-Satz gemerkt (wichtig für den wiederholten Abgleich-Import).
3. **Werte zuordnen:** Für Status, Geschlecht/Anrede, Abteilung und Beitragsklasse alle vorkommenden Werte auflisten
   („x“, „ja“, „1“, „P“, „Herr“ …) und auf die Zielwerte abbilden. Ohne Statusspalte gilt: aktiv, bzw. ausgetreten,
   wenn „Austritt am“ gefüllt ist. Neue Abteilungen und Beitragsklassen kommen ins Einstellungsblatt.
4. **Prüfen und ergänzen:** bearbeitbare Tabelle aller Zeilen. Fehlende Pflichtwerte rot, Filter „nur Zeilen mit
   Problemen“, **Sammel-Ausfüllen** (Zellen markieren → Wert setzen, z. B. Eintritt unbekannt), Zeilen auslassen.
   Geschlecht: Reihenfolge Anrede → Vorname → Mehrheit, geschätzte Zellen markiert mit Zähler
   „12 geschätzt – bitte prüfen“ (Übernahme mit einem Klick). Dazu die bestehenden Plausibilitätsprüfungen
   (`model/checks.py`) und Dubletten. **Weiter erst, wenn alle Pflichtwerte gefüllt sind** (oder die Zeile
   ausgelassen wird).
5. **Ziel:**
   - **Neue Standarddatei:** „Speichern unter“, vorgeschlagen neben dem Original. Einstellungsblatt aus den
     bisherigen QSettings-Auswahlen bzw. Standardwerten (Migration für heutige Nutzer). Nummern 1…n.
   - **Abgleich in eine bestehende Standarddatei:** Zuordnung über Nr (wenn zugeordnet), sonst Name + Vorname +
     Geburtstag (normalisiert). Ähnliche Treffer (gleicher Name, anderer Geburtstag) zur Entscheidung. Ergebnis je
     Mitglied: neu / geändert (je Feld wählen; leere Felder der Datei werden standardmäßig gefüllt, abweichende
     Werte erst nach Entscheidung) / unverändert / **nur in der Datei** (nur Hinweis, nie automatisch ausgetreten;
     Knopf „als ausgetreten markieren“). Geschrieben wird als eine Transaktion (Abschnitt 2), Protokoll-Aktion
     „Import“.
6. **Zusammenfassung:** übernommen, ausgelassen, geschätzt, Hinweis „Original unverändert“. Danach wird die Datei
   geöffnet.

## 5. Oberfläche

- **Startseite:** „Mitgliederliste öffnen“, „Bestehende Liste importieren“, „Neue leere Liste anlegen“ (ersetzt
  „Leere Excel-Vorlage speichern“; erzeugt eine Standarddatei mit allen Blättern), „Zuletzt verwendet“ mit Vereinsname.
- **Kopf:** Vereinsname aus „Einstellungen“, Hinweisleiste (Datei geändert, Konfliktkopie, Löschfrist fällig).
- **Neuer Tab „Mitglieder“:** Tabelle mit Suche, Filter Status/Abteilung, Knöpfe „Neues Mitglied“,
  „Bearbeiten“ (Doppelklick), „Austritt erfassen“.
- **Mitglied-Dialog:** Formular mit Datumsauswahl (leer möglich), Dropdowns, Pflichtfelder markiert,
  Dublettenwarnung, Bereich „Funktionen“ (von/bis), „Weitere Aktionen → endgültig löschen“ (mit Bestätigung).
  Speichern = Transaktion.
- **Einstellungen-Dialog:** bearbeitet das Einstellungsblatt (Anlässe mit Geschenk, Listen, Vereinsname, Löschfrist,
  Erinnerung). Pro PC: Name der bearbeitenden Person.
- **Geburtstage/Ehrungen:** Auswahl aus dem Einstellungsblatt, neue Spalte „Geschenk“ in Vorschau und Export.
- **Datenprüfung (zusätzlich):** fehlende Nr (Knopf „Nummern vergeben“), doppelte Nr, ausgetreten ohne Datum,
  Austrittsdatum bei aktiv/passiv, ungültige Dropdown-Werte, Funktionen ohne passendes Mitglied, Löschfrist fällig,
  Konfliktkopie vorhanden, fehlende Pflichtspalten.
- **Löschfrist:** Hinweis „3 Ausgetretene können gelöscht werden (Austritt vor über 10 Jahren)“ → Liste → Bestätigen.
  Löschen entfernt die Zeile und deren Funktionen, anonymisiert die Protokolleinträge dieser Nr (bleibt nur
  „Nr 123 gelöscht am …“). Hinweis im Dialog: In `Sicherungen/` bleiben die Daten bis zur Rotation (höchstens 12 Monate).

## 6. Code

Neu (Stil wie bisher: kleine Module, Funktionen statt Klassenhierarchien):

| Modul | Inhalt |
|---|---|
| `model/schema.py` | Spalten, Pflicht, Dropdown-Werte, Blattnamen, definierte Namen, Schema-Version (ersetzt `COLUMNS` in `logic/template.py`) |
| `model/club_file.py` | Standarddatei mit openpyxl lesen → Mitglieder, Funktionen, Einstellungen, Datei-ID, Schnappschuss, Excel-Zeilennummern; `is_standard` |
| `store/transaction.py` | Ablauf aus Abschnitt 2 (Vorprüfung, frisch lesen, Abgleich je Feld, Sicherung, atomar schreiben, nachprüfen); `ConflictError` mit Feldunterschieden |
| `store/backups.py`, `store/conflict_copies.py` | Sicherungen und Rotation; Konfliktkopien finden |
| `logic/merge.py` | Zuordnen und Unterschiede je Mitglied (für Abgleich-Import **und** Konfliktkopien) |
| `importer/reader.py`, `importer/mapping.py`, `importer/gender.py` | Lesen (xlsx/xls/csv, Kopfzeile suchen), Spalten-/Wertezuordnung, Trennen, Geschlecht schätzen |
| `resources/first_names.csv` | Vornamenliste (nicht in `data/`, das ist ignoriert) |
| `ui/members_page.py`, `ui/member_dialog.py`, `ui/import_wizard.py`, `ui/merge_dialog.py`, `ui/conflict_dialog.py` | Oberfläche |

Geändert: `Member` (Nr, Geschlecht, Status, Austritt, neue Felder; `member` → `is_member` = Status ≠ ausgetreten),
`model/members.py` (liest Standarddatei über `club_file`; Prüfungen bleiben), `model/columns.py` (Erkennung um neue
Felder erweitern, nur noch für den Import), `logic/template.py` (neue leere Standarddatei),
`ui/settings_dialog.py`/`ui/main_window.py` (Einstellungen aus der Datei, Datei-Überwachung, Import beim Öffnen),
`ui/result_page.py` (Geschenk), `mitgliederverwaltung.py` (`--smoke-test` arbeitet auf einer **Kopie** und prüft
zusätzlich Import, Anlegen, Bearbeiten, Konflikt).

## 7. Tests

- **Automatisch** (`tests/`, mit erfundenen Daten):
  - Schema: leere Datei schreiben → lesen → `is_standard`.
  - Transaktion: Datei unverändert; andere Zeile extern geändert (bleibt erhalten); gleiche Zeile, anderes Feld
    (wird zusammengeführt); gleiches Feld (Konflikt); `~$`-Datei (Abbruch); `PermissionError` beim Ersetzen;
    Sicherung und Rotation; eigene Zusatzspalten und umsortierte Spalten bleiben erhalten; Dropdowns und definierte
    Namen nach dem Schreiben vorhanden.
  - Nummern: vergeben bei leeren Nr; doppelte Nr gemeldet.
  - Import: Titelzeilen vor der Kopfzeile, CSV mit `;` und Windows-1252-Umlauten, „Müller, Hans“, „12345 Ort“,
    Wertezuordnung, Geschlechtsschätzung mit Mehrheit als Rückfall, fehlende Pflichtwerte blockieren, Abgleich über
    Nr und über Name + Geburtstag, „nur in der Datei“ bleibt unverändert.
  - Konfliktkopien: erkannt über die Datei-ID, `Sicherungen/` ausgenommen.
  - Löschfrist, Einstellungsblatt mit Lücken und Standardwerten, Geschenk im Export.
  - UI offscreen: Mitglied anlegen/bearbeiten, Import-Assistent komplett, Konfliktdialog.
- **Von Hand (Checkliste vor dem Release, nur mit erfundenen Daten, z. B. einer Kopie von `example_file.xlsx`):**
  - [ ] Für jedes Programm – Excel Windows, Excel Mac, Excel iOS/Android, Google Tabellen (Datei in Drive, am Handy
    bearbeiten), LibreOffice/Nextcloud Office: ein Mitglied ändern (Datum, Status per Auswahl), eine Zeile ohne Nr
    ergänzen, speichern. Dann in der App: Werte und Daten stimmen, Datenprüfung sinnvoll, „Nummern vergeben“ geht,
    danach in der App etwas speichern und die Datei wieder im Programm öffnen (Auswahllisten noch da, keine
    Reparatur-Meldung).
  - [ ] Datei in Excel geöffnet lassen und in der App speichern: Mac → Rückfrage „trotzdem speichern“; Windows →
    Hinweis, dass die Datei gesperrt ist.
  - [ ] Echte Konfliktkopie erzeugen (Dropbox oder Nextcloud: auf zwei Geräten offline ändern, dann online gehen),
    App öffnen: Kopie wird angeboten, Abgleich übernimmt den Wert, Kopie liegt danach in „Sicherungen“.
  - [ ] Eine echte alte Liste (lokal in `data/`, **nicht committen**) importieren: Zuordnungen und Schätzungen plausibel;
    nur Zähler berichten.
  - [ ] Windows-Installer aus der CI auf einem echten Windows-PC: Import, Speichern, Sicherungen-Ordner.
- Beispieldateien: `example_file.xlsx` im neuen Format, dazu `tests/fixtures/` mit erfundenen Altlisten
  (Titelzeilen, CSV, kombinierte Spalten).

## 8. Reihenfolge (ein Release, auf einem eigenen Branch)

| AP | Inhalt | Aufwand |
|---|---|---|
| 1 | Schema, `club_file` (lesen), neue leere Standarddatei, `Member` umstellen, bestehende Tabs laufen auf dem neuen Modell | M |
| 2 | Transaktion, Sicherungen, Selbstreparatur (nur Backend, viele Tests) | M |
| 3 | Einstellungsblatt lesen/schreiben, Dialog, Geschenk in Listen/Exporten | S–M |
| 4 | Tab „Mitglieder“, Mitglied-Dialog, Austritt, Funktionen, Nummern vergeben, Protokoll, Datei-Überwachung | M–L |
| 5 | Import-Assistent bis „Neue Standarddatei“ (inkl. CSV, Trennen, Werte, Geschlecht, Sammel-Ausfüllen) | L |
| 6 | `logic/merge.py`: Abgleich-Import und Konfliktkopien | M |
| 7 | Löschfrist und endgültiges Löschen | S |
| 8 | Datenprüfung erweitern, Smoke-Test, Beispieldateien, Prüfung von Hand, Doku, Release 0.2.0 | M |

Gesamt grob: mehrere Wochenenden. Nach jedem AP laufen die Tests, und `graphify update .` wird ausgeführt.

### Stand der Umsetzung

- **AP 1 erledigt (2026-11-19, Branch `feature/standard-format`):** `model/schema.py`, `model/club_file.py`,
  `model/values.py`, neue leere Standarddatei (`logic/template.py`), `Member` mit `status`/`is_member` und den neuen
  Feldern, Prüfungen der Standarddatei (Nr fehlt/doppelt, Geschlecht, Status, Austritt). **Übergang:** Alte Listen
  liest `Members` weiter wie bisher (`read_old_list`, „Mitglied“ 1/0 → aktiv/ausgetreten), bis AP 5 sie an den
  Import-Assistenten übergibt. `example_file.xlsx` ist noch im alten Format (AP 8). Offen für AP 3: Datenprüfung
  zeigt „aktiv“ auch für passive Mitglieder, Statistik-Zeile heißt noch „Aktive Mitglieder“.

- **AP 2 erledigt (2026-11-22):** Paket `store/` (siehe Abschnitt 2). Abweichungen/Ergänzungen zum Plan:
  Fehler liegen in `store/errors.py`; Zellen werden ohne Anlegen gelesen (`store/sheet.peek`), damit die Datei nicht
  wächst; fehlen Pflichtspalten in der frischen Datei, bricht das Speichern ab (keine leere Ersatzspalte);
  `save(..., ignore_lock=True)` für „trotzdem speichern“ (z. B. verwaiste `~$`-Datei nach Excel-Absturz), die
  Oberfläche dafür kommt in AP 4. Nachprüfen vergleicht die geschriebenen Bytes.

- **AP 3 erledigt (2026-11-22):** `model/club_settings.py` (Lesen, Spalten per Überschrift, ungültige Werte →
  Datenprüfung mit Name „Blatt „Einstellungen““, Standardwert gilt), `store.changes.update_settings` (Abgleich je
  Bereich: Anlässe, jede Liste, jede allgemeine Einstellung; Bemerkungen bleiben), `ui/club_settings_dialog.py`
  (Reiter Anlässe/Auswahllisten/Allgemein + Name fürs Protokoll; unveränderte Standardwerte werden nicht in die Datei
  geschrieben), `MainWindow.save_change`. Passive zählen je Zweck (`Members.counted`), Geschenk in Vorschau, XLSX
  (Spalte nach dem Datum), TXT und ICS, nicht im datensparsamen Export. Statistik: „Mitglieder“ + „davon passiv“.
  Erinnerung der Datei wird beim Laden gesetzt, Änderung im Reiter gilt nur für den Export. Standard der Erinnerung
  im Einstellungsblatt: 7 Tage (wie bisher in der App).

- **AP 4 erledigt (2026-11-22):** `model/functions.py`, `store.changes.update_functions`/`combine`/`add_member(functions=…)`,
  Tab „Mitglieder“ (zweiter Tab; Suche, Filter Status/Abteilung, alte Listen nur Anzeige), `MemberDialog` (Reiter
  Mitglied / Kontakt und Bank / Funktionen; speichert **nur geänderte Felder**, damit unlesbare Altwerte nicht still
  überschrieben werden; Pflichtprüfung bei neuen Mitgliedern und bei geänderten Pflichtfeldern), `ExitDialog`,
  `ConflictDialog` (je Feld „Ihren Wert“ oder „Wert aus der Datei“), „Nummern vergeben“ (auch beim Bearbeiten eines
  Mitglieds ohne Nr angeboten), `save_change(change, retry)`, Dateiüberwachung (1,5 s Wartezeit, nicht während eines
  Dialogs, nicht nach eigenem Speichern). Funktionen ohne Nr werden über einen eindeutigen Namen zugeordnet und beim
  nächsten Speichern dieses Mitglieds mit Nr geschrieben.

- **AP 5 erledigt (2026-11-22):** Paket `importer/` und `ui/import_wizard.py`. Jede Datei, die nicht im
  Standardformat ist, öffnet beim Laden den Assistenten (`MainWindow.load_file` → `start_import`); Startseite hat
  „Liste … übernehmen“. Vornamenliste als Python-Modul `importer/first_names.py` (statt CSV, nichts extra zu packen).
  Nummern der alten Liste bleiben, wenn gültig und eindeutig. Neue Datei heißt standardmäßig `Mitgliederliste.xlsx`
  neben dem Original. `example_file.xlsx` ist jetzt im Standardformat; die alte liegt als
  `tests/fixtures/old_list.xlsx`. Smoke-Test läuft den Import ohne Dialoge durch. **Noch zu tun (AP 8):** alter Leser
  `Members.read_old_list`, alter `SettingsDialog` und QSettings-Zahlen sind nur noch Übergang/Migration →
  aufräumen; README zum neuen Format.

- **AP 6 erledigt (2026-11-22):** `logic/merge.py` (`FileIndex`, `compare`, `MergeItem`), `store.changes.merge_members`,
  `store/conflict_copies.py`, `ui/merge_dialog.py`, Abgleich-Modus des Assistenten, `MemberActions.merge_list` /
  `check_conflict_copies`. Abweichungen: Zuordnung per Nr nur, wenn auch der Name passt (fremde Nummernkreise);
  ohne Geburtstag in der Liste über einen eindeutigen Namen (für reine E-Mail-/Adresslisten). Konfliktkopien werden
  nur über Dateinamen-Anfang **und** Datei-ID erkannt (keine Namensmuster der Dienste nötig); Funktionen und
  Einstellungen der Kopie werden nicht abgeglichen. Vor einem Abgleich brauchen alle Mitglieder eine Nr. Verschobene
  Konfliktkopien fallen nicht unter die Rotation der Sicherungen.

- **AP 7 erledigt (2026-11-22):** `Members.deletion_due`/`is_due` (Löschfrist ab „Austritt am“, `shift_years`),
  Hinweis in Datenprüfung (nicht gezählt) und Übersicht, `store.changes.delete_members` (Zeile + Funktionen weg,
  frühere Protokollzeilen ohne Name/alt/neu, neue Zeile „gelöscht“), `highest_nr` berücksichtigt das Protokoll,
  `ui/delete_dialog.py`, Einzel-Löschen mit Warnung bei nicht ausgetretenen Mitgliedern (Menü „Weitere …“).
  **Dabei behoben:** Leeren eines Feldes wirkte nicht (`sheet.cell(..., value=None)` setzt in openpyxl nichts) →
  `store.sheet.write_cell`; betraf Mitglied-Dialog (AP 4), Funktionen und Einstellungslisten. Suche nach
  Konfliktkopien übersteht einen verschwundenen Ordner.

- **AP 8 erledigt (2026-11-22):** Aufgeräumt – alter Listen-Leser (`Members` liest nur noch das Standardformat,
  fremde Formate → `MemberListError` mit Hinweis auf den Import; Parameter `config` entfällt), alter
  Einstellungsdialog und `set_numbers`, Erinnerung in `QSettings`, `missing_mandatory`, `since_label`. Die in 0.1
  gewählten Zahlen gehen über `apply_saved_numbers` weiter in neue Dateien. Tests der alten Liste auf Standarddateien
  bzw. `parse_date` umgestellt. Smoke-Test speichert zusätzlich in der importierten Kopie (anlegen, ändern, Sicherung)
  und bricht bei fremden Dateien mit Exit 2 ab statt den Assistenten zu öffnen. Doku: README (neu für Anwender),
  `Release_Notes.md` 0.2.0, `docs/index.html` + `docs/start.png`, `CLAUDE.md` (Festlegungen), `IDEAS.md`.
  **Release 0.2.0 am 2026-11-22** (auf Anweisung von Thomas vor der Prüfliste). Offen: Prüfliste von Hand (Abschnitt 7).

## 9. Doku nach Umsetzung

`CLAUDE.md` (Festlegungen: App schreibt, Standardformat, Einstellungen in der Datei, Transaktion, Löschablauf;
Aufbau-Tabelle), `README.md` (Format, Import, Pflege von Hand, Sicherungen, Konfliktkopien, Löschfrist),
`Release_Notes.md`, `IDEAS.md` (31–36/45 → hierher, 39 entfällt), Download-Seite falls Screenshots sich ändern.

## 10. Geklärte Detailpunkte (2026-11-19)

1. **Passive Mitglieder:** pro Verein im Einstellungsblatt, getrennt für Geburtstage, Ehrungen und Statistik
   (Standard ja). „Ausgetreten“ zählt nie.
2. **Vornamenliste:** klein anfangen mit einer selbst zusammengestellten Liste häufiger Vornamen
   (`resources/first_names.csv`), keine fremde Datenbank übernehmen; nach und nach ergänzen. Unbekannte Namen →
   Mehrheit, markiert.
3. **Änderungsprotokoll:** vorerst unbegrenzt (später ggf. Einträge älter als die Löschfrist entfernen).
4. **Eintritt unbekannt:** bleibt Pflicht; im Import per Sammel-Ausfüllen (z. B. 01.01. des Gründungsjahrs).

Nicht Teil dieses Releases: Dateien je Mitglied (36), Ehrungs-Historie (bewusst nicht), SEPA, Serienbriefe,
Statistik nach Geschlecht (später leicht möglich, weil das Feld dann Pflicht ist).
