# CLAUDE.md — member-admin ("Mitglieder Management Portal")

Desktop-App für den Vereinsvorstand: pflegt die Mitglieder in einer Excel-Datei und erzeugt daraus Geburtstags-,
Ehrungslisten und Statistik. Gebaut von Thomas Egen; Nachfolger sind **nicht technik-affin** → Einfachheit der
Bedienung und der Installation hat Vorrang vor Features. Sprache im Gespräch: Deutsch. Code, Commits, Bezeichner:
Englisch. UI-Texte sind deutsch (Anrede „Sie“). **Die Excel-Datei ist der Datenspeicher** (geteilt über
Dropbox/OneDrive/Google Drive/Nextcloud, auch ohne App bearbeitet, z. B. am Smartphone); die App schreibt seit 0.2
hinein, aber nur über `store/` (sicheres Speichern). Konzept und Entscheidungen: `PLAN_DATA_STORAGE.md`.

## Was die App kann
- Start: Mitgliederliste öffnen (Dialog, Drag & Drop oder „Zuletzt verwendet“). Die App arbeitet nur mit dem **Standardformat**; jede andere Liste (`.xlsx`, `.xls`, `.csv`) öffnet den **Import-Assistenten** (Datei → Spalten → Werte → Prüfen/Ergänzen → neue Datei speichern; Original bleibt unverändert). „Neue leere Mitgliederliste anlegen“ schreibt eine leere Standarddatei.
- **Auswertungsjahr** im Kopf (Standard: ab Oktober das Folgejahr). Es steuert Geburtstage, Ehrungen, „Neue Mitglieder“.
- Tabs: Übersicht (mit „Demnächst“: nächste 30 Tage; Hinweis auf fällige Löschfrist) · **Mitglieder** (Suche, Filter; anlegen, bearbeiten inkl. Funktionen, Austritt, Nummern vergeben; unter „Weitere …“ „Liste abgleichen“ (z. B. Verbandsexport, E-Mail-Liste) und „endgültig löschen“; „Konfliktkopie prüfen“, wird nach dem Öffnen einmal pro Start angeboten) · Geburtstage · Ehrungen · Statistik · Datenprüfung.
- Die geöffnete Datei wird überwacht (`QFileSystemWatcher`): Änderungen von außen (Excel, Sync) werden automatisch neu eingelesen.
- **Einstellungen** (Knopf im Kopf) stehen im Blatt „Einstellungen“ der Datei (Anlässe mit Geschenk, Auswahllisten, Vereinsname, Löschfrist, Erinnerung, ob Passive zählen; `ClubSettingsDialog`). Auf dem PC (`QSettings`) nur: zuletzt verwendete Datei, Name fürs Protokoll; die in 0.1 gewählten Zahlen gehen in neue/importierte Dateien über. `config.ini` liefert nur Standardwerte.
- Löschfrist (Standard „nie“): fällige Ausgetretene erscheinen in Übersicht/Datenprüfung, Knopf „Löschfrist: n löschen …“; Löschen nur nach Bestätigung, entfernt Zeile + Funktionen, anonymisiert das Protokoll; gelöschte Nr werden nie wieder vergeben (`store.changes.highest_nr` liest auch das Protokoll).
- Geburtstage/Ehrungen: ganzes Jahr oder eigener Zeitraum, Auswahl der runden Zahlen,
  **Vorschau-Tabelle** (sortierbar, mit Geschenk), Export als TXT, Excel (XLSX) und ICS (Ganztagstermine, stabile UIDs, Erinnerung n Tage vorher),
  Option „Nur Name und Anlass“ (datensparsam, für TXT/XLSX, ohne Geschenk).
- Datenprüfung: alle Auffälligkeiten mit **Excel-Zeilennummer** (fehlende Pflichtangaben, ungültiger Status/Geschlecht,
  Nr fehlt/doppelt, nicht lesbares Datum, Alter unplausibel, Eintritt vor Geburt/weit in der Zukunft, Austritt ohne Datum,
  mögliche Dublette = gleicher Name **und** Geburtstag, Probleme in den Blättern Einstellungen/Funktionen, fällige Löschfrist);
  Standard ohne Ausgetretene.
- Statistik: Mitglieder (davon passiv), Neue, Altersgruppen (Verbandsgruppen bis 6/7–14/15–18/19–26/27–40/41–60/über 60), Durchschnittsalter, Export XLSX.
- Es zählen aktive Mitglieder, passive je nach Einstellung des Vereins (Geburtstage/Ehrungen/Statistik getrennt).

## Aufbau
| Pfad | Zweck |
|---|---|
| `mitgliederverwaltung.py` | Einstieg (`main`), `--smoke-test <excel>` für den Build (lädt Standarddatei, schreibt alle Exporte und eine Vorlage, importiert die Datei und speichert in der Kopie; die Datei selbst bleibt unverändert; Exit 0/2, fremde Datei → 2), `--screenshots=<ordner> <excel>` (Bild je Tab); beide mit eigenen, leeren `QSettings` |
| `config/config.py` | `Config`, `ConfigError`, `parse_numbers`; `config.ini` neben EXE/`.app`, sonst eingebaute Vorlage, sonst Projektordner, sonst `DEFAULTS` (Datei ist optional) |
| `config.ini` | Standardwerte: Auswahllisten (Geburtstage/Ehrungen) neuer Dateien + bevorzugte Spaltennamen für den Import |
| `model/members.py` | Standarddatei → `Members` (Mitglieder, `Issue`s, Einstellungen, Funktionen, `snapshot`, `file_id`, `counted`, `deletion_due`), `MemberListError` (auch für fremde Formate) |
| `model/schema.py`, `model/club_file.py`, `model/values.py` | **Standardformat** (Blätter, Spalten, Dropdown-Werte, Schema-Version), Lesen der Standarddatei mit openpyxl (echte Excel-Zeilen, `is_standard_file`), `parse_date`/`to_text`. Plan: `PLAN_DATA_STORAGE.md` |
| `store/transaction.py`, `store/changes.py`, `store/repair.py`, `store/backups.py`, `store/sheet.py`, `store/errors.py` | **Sicheres Schreiben**: `save(path, change, editor)` = Sperrdatei prüfen, frisch einlesen, Änderung (`update_member` mit Abgleich je Feld, `add_member`, `assign_numbers`), Selbstreparatur, Protokoll, Sicherung in `Sicherungen/`, atomar ersetzen, nachprüfen. Fehler: `SaveError`, `FileLocked`, `Conflict`, `Duplicate` |
| `model/columns.py`, `model/checks.py`, `model/issue.py` | Spaltenerkennung für den Import (`FIELDS`, `detect_columns`, `normalize`), Plausibilitätsprüfungen (`age_on`), `Issue` |
| `model/member.py`, `model/entry.py` | Datenklassen (`Member`, `Entry` = Treffer mit Zahl, Mitglied, Datum) |
| `logic/date_utils.py` | `shift_years` (29.02. → 28.02. in Nicht-Schaltjahren) |
| `logic/birthday_calculation.py`, `logic/honor_calculation.py` | `find_*`, `is_*`, TXT-/ICS-Export |
| `logic/export.py`, `logic/calendar_export.py` | XLSX-Export (auch `minimal`), ICS-Export (ein Writer für Geburtstage und Ehrungen, `VALARM`) |
| `logic/upcoming.py`, `logic/statistics.py`, `logic/template.py` | „Demnächst“, Statistik, leere Standarddatei (alle Blätter, Dropdowns, definierte Namen, Datei-ID) |
| `ui/main_window.py` | Hauptfenster, Laden, Jahr, Drag & Drop (`show_error` überschreibbar für Tests) |
| `ui/result_page.py` | **eine** Seite für Geburtstage und Ehrungen (`ResultSpec`), Vorschau, Speichern |
| `ui/overview_page.py`, `ui/statistics_page.py`, `ui/issues_page.py`, `ui/welcome_page.py`, `ui/theme.py` | Übersicht, Statistik, Datenprüfung, Startseite, Stil |
| `model/club_settings.py`, `ui/club_settings_dialog.py` | Einstellungsblatt lesen (`ClubSettings`, `read_settings`, Hinweise bei ungültigen Werten), Dialog dazu; `MainWindow.save_change` = gemeinsamer Speicherablauf (Name fürs Protokoll, „trotzdem speichern“ bei Sperrdatei, neu einlesen) |
| `model/functions.py` | Blatt „Funktionen“ lesen (`Function`, Zuordnung per Nr oder eindeutigem Namen, Hinweise) |
| `ui/members_page.py`, `ui/member_dialog.py`, `ui/member_actions.py`, `ui/conflict_dialog.py` | Tab „Mitglieder“, Mitglied-Dialog (speichert nur geänderte Felder; `DateField` darf leer sein), Austritts-Dialog, Abläufe mit Dubletten-Rückfrage und Konfliktdialog je Feld |
| `ui/saving.py` | gemeinsamer „Speichern unter“-Ablauf für Exporte |
| `tests/test_regressions.py`, `tests/test_ui.py`, `tests/test_store.py`, `tests/test_import.py` | Tests (Logik/Modell; Oberfläche offscreen; Schreiben; Import) |
| `build.py`, `.github/workflows/release.yml` | PyInstaller → `release/` (Windows: `-Windows-Setup.exe` + `-Windows.zip`, macOS: `-Mac.dmg`; Dateinamen ohne Version) |
| `installer/windows.iss` | Inno-Setup-Skript (Installation pro Benutzer ohne Admin, `AppId` nie ändern) |
| `docs/` | Download-Seite für GitHub Pages (`index.html`, `start.png`, `qr-download.svg`), verlinkt `releases/latest/download/…` |
| `importer/` | Import: `reader` (xlsx/xls/csv, Zeichensatz, Trennzeichen), `mapping` (Kopfzeile, Spalten-/Wertevorschläge, „Name, Vorname“ und „PLZ Ort“ trennen, `convert`, Nummern), `gender` + `first_names` (Geschlecht schätzen), `writer` (neue Standarddatei) |
| `ui/import_wizard.py` | Import-Assistent (5 Schritte, Sammel-Ausfüllen, Schätzungen bestätigen); mit `merge_target` Abgleich mit der offenen Datei (vorhandene Personen brauchen keine vollständigen Daten) |
| `ui/delete_dialog.py` | Liste der zu löschenden Mitglieder (Löschfrist), `store.changes.delete_members` |
| `logic/merge.py`, `store/conflict_copies.py`, `ui/merge_dialog.py` | Abgleich je Person (Nr nur zusammen mit dem Namen, sonst Name+Geburtstag, ohne Geburtstag eindeutiger Name; leere Werte löschen nie), `store.changes.merge_members`; Konfliktkopien (gleicher Dateianfang + Datei-ID) finden, abgleichen, nach `Sicherungen/` verschieben |
| `example_file.xlsx` | Beispielliste im **Standardformat** (10 erfundene Personen, wird mit der App ausgeliefert, Smoke-Test/Screenshots) |
| `tests/fixtures/old_list.xlsx` | alte Beispielliste (Format vor 0.2) für Import-Tests |

Berechnung: Geburtstag n im Zeitraum, wenn das Geburtsdatum zwischen `von − n Jahre` und `bis − n Jahre` liegt.
Ehrung n analog mit „Eintritt“.

## Entwickeln (macOS/Windows)
- Stack: Python 3.12, **PySide6 (Qt)** — bewusst statt Tk/customtkinter (Tk fehlt in Homebrew-/System-Python, hässliche Datumsfelder, kein Offscreen-Test).
- Setup: `uv venv --python 3.12 .venv && uv pip install --python .venv/bin/python -r requirements-dev.txt`
- Start: `.venv/bin/python mitgliederverwaltung.py [excel]`
- Tests: `.venv/bin/python tests/test_regressions.py`, `tests/test_ui.py`, `tests/test_store.py` und `tests/test_import.py` (UI-Tests lassen einen unerwartet geöffneten Import-Assistenten scheitern statt zu hängen)
  (Oberfläche läuft mit `QT_QPA_PLATFORM=offscreen`, auch für Screenshots per `widget.grab().save(...)`).
- Build lokal: `.venv/bin/python build.py <version>` → `release/` (ignoriert; Mac-DMG; Windows-Installer nur mit Inno Setup 6). Danach gepackte App prüfen:
  `QT_QPA_PLATFORM=offscreen release/Mitgliederverwaltung.app/Contents/MacOS/Mitgliederverwaltung --smoke-test example_file.xlsx`
- Scratch-Skripte nie `inspect.py`, `json.py` o. Ä. nennen (überdecken die Standardbibliothek).

## Regeln für Änderungen
- **Personenbezogene Daten:** Echte Mitgliederlisten nie committen, nie in Logs/Chat ausgeben, auch keine Screenshots davon.
  Lokale Listen liegen in `data/` (ignoriert, ebenso `*.xlsx` außer `example_file.xlsx`). Für Screenshots/Tests erfundene Daten nehmen.
  Auswertungen der echten Liste nur als Zähler/Zeilennummern berichten.
- **Zeilenenden: LF** (`.gitattributes`). Nicht massenhaft umformatieren.
- Kleine Diffs, bestehenden Stil beibehalten. Keine Architekturänderung ohne Rückfrage.
- Committen/Pushen/Release (Workflow-Dispatch, Tags) nur auf ausdrückliche Anweisung.
- Änderungen an Excel-Spalten oder `config.ini`-Schlüsseln immer mit `README.md`, `example_file.xlsx` und Tests abgleichen.
- Neue Version → `Release_Notes.md` ergänzen. Nach Codeänderungen `graphify update .` (siehe unten).

## Festlegungen (nicht rückgängig machen)
- Geburtstag am **29.02.** wird in Nicht-Schaltjahren am **28.02.** gefeiert (`shift_years`; Zeitraumgrenzen, ICS, Ehrungen).
- Datumsspalten in Excel: echte Daten; **Zahlen = Excel-Seriennummer** (28353 = 16.08.1977; pandas würde sie sonst als 1970 lesen);
  ISO-Text (`1967-06-01`) bleibt ISO, deutscher Text (`13.02.1970`) wird tag-zuerst gelesen (`dayfirst=True` allein vertauscht ISO!).
- Spalten werden **immer über die Überschrift** gefunden (normalisiert: Groß-/Kleinschreibung, Leer-/Sonderzeichen, ß/Umlaute egal), auch im Standardformat: Spalten dürfen verschoben, eigene ergänzt werden. Eine Spalte gehört zu genau einem Feld.
- Pflichtspalten fehlen → `MemberListError` mit fehlenden Namen **und** den gefundenen Überschriften; beim Speichern `SaveError` (keine leere Ersatzspalte). Leere Zeilen werden übersprungen.
- Fehlende Daten erzeugen keine Dialoge, sondern `Issue`s (Datenprüfung); fehlendes Datum = `NaT`, Person wird übersprungen.
- Leerer/ungültiger Status → Hinweis, Mitglied zählt nicht. „m“/„w“/„d“ und Groß-/Kleinschreibung werden akzeptiert, „a“ nicht (aktiv/ausgetreten).
- **Schreiben nur über `store.transaction.save`**: Sperrdatei (`~$`, `.~lock.`) prüfen, frisch einlesen, Abgleich je Feld (dreiseitig gegen `Members.snapshot`), Selbstreparatur, Protokoll, Sicherung `Sicherungen/<Name> JJJJ-MM-TT HHMMSS.xlsx` (letzte 30 + erste je Monat für 12 Monate), temporäre Datei `~$member-admin-*.tmp` + `os.replace`, Bytes nachprüfen. Änderung ohne Protokolleintrag schreibt nichts.
- Zellen in einer zum Schreiben geöffneten Mappe nur über `peek`/`sheet_rows` lesen (sonst legt openpyxl leere Zellen an) und über `write_cell` schreiben (`sheet.cell(..., value=None)` leert **nicht**).
- Die **Nr** ist die stabile ID: vergibt die App, nie wieder verwendet (auch nicht nach Löschen); Zeilen werden per Nr gefunden.
- Dialoge speichern **nur geänderte Felder** (unlesbare Altwerte bleiben); leere Werte aus Importen/Abgleichen löschen nie etwas.
- Dropdowns mit Vereinslisten über **definierte Namen** (`Abteilungen`, …), nicht über Blattverweise (würde openpyxl verwerfen); Fehlerstil „warning“.
- Import: Original bleibt unverändert; Geschlecht wird nur geschätzt **und** muss bestätigt werden; Nr der alten Liste bleiben, wenn gültig und eindeutig. Abgleich per Nr nur, wenn auch der Name passt. **Unbekannte Daten** (Geburtstag, Eintritt, Austritt am) blockieren den Import nicht (`importer.mapping.MAY_STAY_EMPTY`, `ImportRow.gaps`), sondern landen leer in der Datei und in der Datenprüfung (Entscheidung Thomas 2026-11-22); im Mitglied-Dialog bleiben sie für neue Mitglieder/Austritte Pflicht.
- TXT: UTF-8, `newline=""` (sonst `\r\r\n` unter Windows). Keine Personendaten in `print`/Logs.
- ICS: Ganztagstermine, UID aus Name+Datum+Zahl (erneuter Import erzeugt keine Dubletten; Ehrungen mit Präfix `honor|`). Erinnerung = 9 Uhr, n Tage vorher.
- Keine IBAN-Prüfung: in der echten Liste enthält die Spalte „IBAN“ reine Zahlen (Prüfziffer würde fast jede Zeile melden).
- Build schreibt nach `release/` (nicht `dist/`/`build/`: dort liegen alte Windows-Artefakte, `Mitgliederverwaltung` kollidiert auf macOS mit `mitgliederverwaltung`).

## Verteilung / offene Punkte (Stand 2026-11-22)
- **Unsigniert:** Windows zeigt SmartScreen, macOS-Gatekeeper lehnt die App ab (`spctl: rejected`, geprüft). README erklärt das Öffnen.
  Echte Lösung wäre Apple Developer ID + Notarisierung und eine Windows-Signatur (kostet Geld).
  **Entscheidung Thomas (2026-11-14): vorerst nicht signieren.** Nicht erneut vorschlagen, außer er fragt danach.
- Ideenliste mit Priorisierung: `IDEAS.md`.
- macOS-Build nur Apple Silicon (`macos-latest`). **Entscheidung Thomas (2026-11-17): Intel-Mac nicht nötig.**
- **Release 0.1.0 veröffentlicht (2026-11-17)** über den Workflow (alle Jobs grün, inkl. stiller Installation + Smoke-Test unter Windows und Smoke-Test aus dem DMG).
  Download-Seite live: https://tomegen.github.io/member-admin/ (GitHub Pages aus `main` / `/docs`); `releases/latest/download/…`-Links geprüft (HTTP 200).
  Noch nicht von Hand auf einem echten Windows-PC installiert; Windows-Screenshots aus CI sehen sauber aus (Tabellenköpfe etwas kleiner als auf dem Mac).
- Windows lokal testen (Docker/VM): **laut Thomas nicht nötig** (Mac-Docker kann keine Windows-Container); Windows-Prüfung über CI.
- **Release 0.2.1 (2026-11-22):** unbekannte Daten blockieren den Import nicht mehr, Vornamenliste erweitert (Test mit echter Liste).
- **Release 0.2.0 (2026-11-22)** auf Wunsch von Thomas **vor** der Prüfliste von Hand veröffentlicht (Standardformat, Pflege, Import, Abgleich, Löschfrist; AP 1–8 in `PLAN_DATA_STORAGE.md`). Thomas testet danach die offizielle Mac-Version mit einer echten Liste. Prüfliste (Excel Win/Mac/mobil, Google Tabellen, LibreOffice, echte Konfliktkopie, Windows-PC) aus `PLAN_DATA_STORAGE.md` Abschnitt 7 ist **noch offen**; Fehler daraus → 0.2.x.
- Dateien je Mitglied (`IDEAS.md` 36) und 37–49 sind **nur notiert** → nur nach Freigabe.
- Projektordner liegt seit 2026-11-22 unter `~/Documents/private/Programmieren/projects/member-admin` (vorher `…/private/Documents/Programmieren/…`).

## Neuer Chat — so einsteigen
1. `git status` und `git fetch` prüfen, bevor etwas geändert wird.
2. Diese Datei lesen; Codefragen zuerst mit `graphify query`.
3. Bei Auswertungen (z. B. Jahr 2027): Excel in der App wählen lassen; Ergebnisse nur lokal ablegen, nicht committen.
4. Testdaten immer erfunden: `example_file.xlsx` (Standard), `tests/fixtures/old_list.xlsx` (altes Format).

## graphify

This project has a knowledge graph at graphify-out/ with god nodes, community structure, and cross-file relationships.

Rules:
- When graphify-out/graph.json exists, run `graphify query "<question>"` before your first grep, search or source-file read for a codebase question, and put this rule in every subagent prompt that explores code. Read raw files only for lines the graph or an earlier read already located. Use `graphify path "<A>" "<B>"` for relationships and `graphify explain "<concept>"` for focused concepts. These return a scoped subgraph, usually much smaller than GRAPH_REPORT.md or raw grep output.
- If graphify-out/wiki/index.md exists, use it for broad navigation instead of raw source browsing.
- Read graphify-out/GRAPH_REPORT.md only for broad architecture review or when query/path/explain do not surface enough context.
- After modifying code, run `graphify update .` to keep the graph current (AST-only, no API cost).
- A committed graphify-out/graph.json is rewritten whole on every build, so a large diff to it in a pull request is expected. Do not flag it as churn or suggest skipping the graph rebuild or its hooks.
