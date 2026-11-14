# CLAUDE.md — member-admin ("Mitglieder Management Portal")

Desktop-App für den Vereinsvorstand: liest eine Mitglieder-Excel und erzeugt daraus Geburtstags- und
Ehrungslisten. Gebaut von Thomas Egen; Nachfolger sind **nicht technik-affin** → Einfachheit der Bedienung
und der Installation hat Vorrang vor Features. Sprache im Gespräch: Deutsch. Code, Commits, Bezeichner: Englisch.
UI-Texte sind deutsch (Anrede „Sie“). **Die Excel-Liste bleibt der Datenspeicher** (Vorstände pflegen sie
auch ohne die App, z. B. am Smartphone) — die App liest sie nur, schreibt nie hinein.

## Was die App kann
- Start: Excel wählen (Dialog, Drag & Drop oder „Zuletzt verwendet“); `.xlsx`/`.xls`, erstes Blatt, Kopfzeile = Spaltennamen.
- **Auswertungsjahr** im Kopf (Standard: ab Oktober das Folgejahr). Es steuert Geburtstage, Ehrungen, „Neue Mitglieder“.
- Tabs: Übersicht · Geburtstage · Ehrungen · Datenprüfung.
- Geburtstage/Ehrungen: ganzes Jahr oder eigener Zeitraum, Auswahl der runden Zahlen (aus `config.ini`),
  **Vorschau-Tabelle** (sortierbar), Export als TXT, Excel (XLSX), bei Geburtstagen zusätzlich ICS (Ganztagstermine, stabile UIDs).
- Datenprüfung: alle unvollständigen Zeilen mit **Excel-Zeilennummer** (fehlender Geburtstag/„Mitglied seit“,
  ungültiger Mitglied-Status, nicht lesbares Datum); Standard nur aktive Mitglieder. „Neu einlesen“ nach Korrektur in Excel.
- Nur Mitglieder mit `Mitglied = 1` zählen.

## Aufbau
| Pfad | Zweck |
|---|---|
| `mitgliederverwaltung.py` | Einstieg (`main`), `--smoke-test <excel>` für den Build (lädt Datei, schreibt alle Exporte, Exit 0/2) |
| `config/config.py` | `Config`, `ConfigError`; `config.ini` neben EXE/`.app`, sonst eingebaute Vorlage, sonst Projektordner |
| `config.ini` | Auswahllisten (Geburtstage/Ehrungen) + Excel-Spaltennamen |
| `model/members.py` | Excel → `Member`-Liste, `Issue`-Liste (Datenprüfung), `parse_date`, `MemberListError`, Zähler |
| `model/member.py`, `model/entry.py` | Datenklassen (`Member`, `Entry` = Treffer mit Zahl, Mitglied, Datum) |
| `logic/date_utils.py` | `shift_years` (29.02. → 28.02. in Nicht-Schaltjahren) |
| `logic/birthday_calculation.py`, `logic/honor_calculation.py` | `find_*`, `is_*`, TXT-/ICS-Export |
| `logic/export.py` | XLSX-Export, Tabellenzeilen |
| `ui/main_window.py` | Hauptfenster, Laden, Jahr, Drag & Drop (`show_error` überschreibbar für Tests) |
| `ui/result_page.py` | **eine** Seite für Geburtstage und Ehrungen (`ResultSpec`), Vorschau, Speichern |
| `ui/overview_page.py`, `ui/issues_page.py`, `ui/welcome_page.py`, `ui/theme.py` | Übersicht, Datenprüfung, Startseite, Stil |
| `tests/test_regressions.py`, `tests/test_ui.py` | Tests (Logik/Modell; Oberfläche offscreen) |
| `build.py`, `.github/workflows/release.yml` | PyInstaller → `release/*.zip` (Windows-EXE, macOS-App) |
| `example_file.xlsx` | Beispielliste mit den erwarteten Spalten (Fake-Daten) |

Berechnung: Geburtstag n im Zeitraum, wenn das Geburtsdatum zwischen `von − n Jahre` und `bis − n Jahre` liegt.
Ehrung n analog mit „Mitglied seit“.

## Entwickeln (macOS/Windows)
- Stack: Python 3.12, **PySide6 (Qt)** — bewusst statt Tk/customtkinter (Tk fehlt in Homebrew-/System-Python, hässliche Datumsfelder, kein Offscreen-Test).
- Setup: `uv venv --python 3.12 .venv && uv pip install --python .venv/bin/python -r requirements-dev.txt`
- Start: `.venv/bin/python mitgliederverwaltung.py [excel]`
- Tests: `.venv/bin/python tests/test_regressions.py` und `.venv/bin/python tests/test_ui.py`
  (Oberfläche läuft mit `QT_QPA_PLATFORM=offscreen`, auch für Screenshots per `widget.grab().save(...)`).
- Build lokal: `.venv/bin/python build.py <version>` → `release/` (ignoriert). Danach gepackte App prüfen:
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
- Pflichtspalten fehlen → `MemberListError` mit Spaltennamen. Alle anderen Spalten sind optional. Leere Zeilen werden übersprungen.
- Fehlende Daten erzeugen keine Dialoge, sondern `Issue`s (Datenprüfung); fehlendes Datum = `NaT`, Person wird übersprungen.
- Leerer/ungültiger „Mitglied“-Wert → Hinweis, Mitglied zählt nicht.
- TXT: UTF-8, `newline=""` (sonst `\r\r\n` unter Windows). Keine Personendaten in `print`/Logs.
- ICS: Ganztagstermine, UID aus Name+Datum+Zahl (erneuter Import erzeugt keine Dubletten).
- Build schreibt nach `release/` (nicht `dist/`/`build/`: dort liegen alte Windows-Artefakte, `Mitgliederverwaltung` kollidiert auf macOS mit `mitgliederverwaltung`).

## Verteilung / offene Punkte (Stand 2026-11-14)
- **Unsigniert:** Windows zeigt SmartScreen, macOS-Gatekeeper lehnt die App ab (`spctl: rejected`, geprüft). README erklärt das Öffnen.
  Echte Lösung wäre Apple Developer ID + Notarisierung und eine Windows-Signatur (kostet Geld).
  **Entscheidung Thomas (2026-11-14): vorerst nicht signieren.** Nicht erneut vorschlagen, außer er fragt danach.
- Ideenliste mit Priorisierung: `IDEAS.md`.
- macOS-Build nur Apple Silicon (`macos-latest`); Intel-Macs bräuchten einen eigenen Runner.
- Workflow `release.yml` ist **nicht auf GitHub getestet** (nur lokal gebaut/Smoke-Test auf macOS, YAML geprüft). Windows-Build ungeprüft.
- Ideen: Excel-Vorlage mit Dropdown für „Mitglied“, Spalten automatisch erkennen statt `config.ini`, PWA/Web-Variante für Smartphone.

## Neuer Chat — so einsteigen
1. `git status` und `git fetch` prüfen, bevor etwas geändert wird.
2. Diese Datei lesen; Codefragen zuerst mit `graphify query`.
3. Bei Auswertungen (z. B. Jahr 2027): Excel in der App wählen lassen; Ergebnisse nur lokal ablegen, nicht committen.

## graphify

This project has a knowledge graph at graphify-out/ with god nodes, community structure, and cross-file relationships.

Rules:
- When graphify-out/graph.json exists, run `graphify query "<question>"` before your first grep, search or source-file read for a codebase question, and put this rule in every subagent prompt that explores code. Read raw files only for lines the graph or an earlier read already located. Use `graphify path "<A>" "<B>"` for relationships and `graphify explain "<concept>"` for focused concepts. These return a scoped subgraph, usually much smaller than GRAPH_REPORT.md or raw grep output.
- If graphify-out/wiki/index.md exists, use it for broad navigation instead of raw source browsing.
- Read graphify-out/GRAPH_REPORT.md only for broad architecture review or when query/path/explain do not surface enough context.
- After modifying code, run `graphify update .` to keep the graph current (AST-only, no API cost).
- A committed graphify-out/graph.json is rewritten whole on every build, so a large diff to it in a pull request is expected. Do not flag it as churn or suggest skipping the graph rebuild or its hooks.
