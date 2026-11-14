# CLAUDE.md — member-admin ("Mitglieder Management Portal")

Desktop-Tool für den Vereinsvorstand: liest eine Mitglieder-Excel und erzeugt daraus Geburtstags- und
Ehrungslisten. Gebaut von Thomas Egen; Nachfolger sind **nicht technik-affin** → Einfachheit der Bedienung
und der Installation hat Vorrang vor Features. Sprache im Gespräch: Deutsch. Code, Commits, Bezeichner: Englisch.
UI-Texte sind deutsch (teils noch englisch, siehe Verbesserungsliste).

## Was das Tool kann
- Start: Dateidialog für die Mitgliederliste (`.xlsx`/`.xls`, erstes Blatt, Kopfzeile = Spaltennamen).
- Startseite: Anzahl aktueller Mitglieder (Summe der Spalte „Mitglied“, 0/1) und **neue Mitglieder im aktuellen
  Kalenderjahr** (Jahr kommt von `Timestamp.now()`, nicht wählbar).
- Geburtstage: Zeitraum (von/bis) + Auswahl der runden Geburtstage (`config.ini`) → `.txt` oder `.ics` (Kalender).
- Ehrungen: Zeitraum + Auswahl der Mitgliedsjahre (`config.ini`) → `.txt`.
- Nur Mitglieder mit `Mitglied = 1` werden berücksichtigt.

## Aufbau
| Pfad | Zweck |
|---|---|
| `mitgliederverwaltung.py` | Einstieg, `MemberAdminApp` (customtkinter), Dateidialog, Seitenwechsel |
| `config/config.py` | liest `config.ini` (relativ zum **aktuellen Arbeitsverzeichnis**) |
| `config.ini` | Auswahllisten für Geburtstage/Ehrungen + Excel-Spaltennamen |
| `model/members.py` | Excel → `Member`-Liste, Mitgliederzahlen |
| `model/member.py` | Datenklasse + Textausgabe (`print`) |
| `logic/date_utils.py` | `shift_years` (Datum um Jahre verschieben, 29.02. → 28.02.) |
| `logic/birthday_calculation.py` | `is_birthday`, TXT-/ICS-Export |
| `logic/honor_calculation.py` | `is_honor`, TXT-Export |
| `ui/*.py` | `StartPage`, `BirthdayPage`, `HonorPage` |
| `build.py`, `.github/workflows/build-exe.yml` | PyInstaller-Build; Release per manuellem Workflow-Dispatch (Windows-EXE, Tag = Version) |
| `example_file.xlsx` | Beispielliste mit den erwarteten Spalten |

Berechnung: Geburtstag n im Zeitraum, wenn `geburtsdatum` zwischen `von − n Jahre` und `bis − n Jahre` liegt.
Ehrung n analog mit „Mitglied seit“.

## Lokal ausführen (macOS)
- Das System-Python (3.9) und Homebrew-Python ohne Tk reichen **nicht**. Es braucht Python ≥ 3.10 **mit Tk**
  (z. B. `brew install python-tk@3.x`) und ein venv:
  `python3 -m venv .venv && .venv/bin/pip install pandas openpyxl xlrd icalendar customtkinter tkcalendar`
- Start: `.venv/bin/python mitgliederverwaltung.py` **aus dem Repo-Ordner** (wegen `config.ini`).
- Rechenlogik lässt sich ohne GUI testen (`logic/*`, `model/*`); `tkinter` dafür ggf. stubben.

## Regeln für Änderungen
- **Personenbezogene Daten:** Echte Mitgliederlisten nie committen, nie in Logs/Chat ausgeben. Nur
  `example_file.xlsx` (Fake-Daten) liegt im Repo. Neue Excel-Dateien vor dem Commit prüfen.
- **Zeilenenden: LF.** Ein Windows-Checkout (CRLF) hat früher den ganzen Working Tree als „geändert“ markiert.
  Nicht massenhaft umformatieren.
- Kleine Diffs, bestehenden Stil beibehalten, nur ändern was nötig ist. Keine Architekturänderung ohne Rückfrage.
- Committen/Pushen/Release (Workflow-Dispatch, Tags) nur auf ausdrückliche Anweisung.
- Änderungen an Excel-Spalten oder `config.ini`-Schlüsseln immer mit `README.md` und `example_file.xlsx` abgleichen.
- Neue Version → `Release_Notes.md` ergänzen (zuletzt dokumentiert: 0.0.3; Tags existieren bis 0.0.7).

## Tests
`python tests/test_regressions.py` (nur Standardbibliothek + pandas; fehlt Tk, wird `tkinter` gestubbt).
Abgedeckt: Schalttag, Zeiträume über den Jahreswechsel, Ehrungen, UTF-8-Ausgabe, fehlende/optionale Spalten,
leere „Mitglied“-Zelle, Neue Mitglieder je Jahr, Config unabhängig vom Arbeitsverzeichnis, keine Personendaten in der Konsole.
Nach Änderungen an `logic/` oder `model/` ausführen und bei neuen Fehlern einen Test ergänzen.

## Festlegungen (2026-11-14 behoben, nicht rückgängig machen)
- Geburtstag am **29.02.** wird in Nicht-Schaltjahren am **28.02.** gefeiert (`logic/date_utils.shift_years`);
  das gilt für Zeitraumgrenzen, ICS-Termine und Ehrungen.
- Pflichtspalten (Name, Vorname, Geburtstag, Mitglied seit, Mitglied) fehlen → Fehlerfenster mit Spaltennamen
  (`MemberListError`). Alle anderen Spalten sind wirklich optional.
- Leere oder ungültige „Mitglied“-Zelle → Warnung, Mitglied wird nicht gezählt.
- `config.ini` wird neben der EXE bzw. im Projektordner gesucht, nicht im Arbeitsverzeichnis. Fehlt sie, endet die App nach der Meldung.
- TXT-Dateien: UTF-8, `newline=""` (sonst doppelte `\r` unter Windows, da `os.linesep` im Text steckt).
- Keine Personendaten in `print`/Logs.

## Offene Verbesserungen (Auswahl, Stand 2026-11-14)
- Bedienung: Jahr-Auswahl statt zweier Datumsfelder, macOS-App/einfacher Download, UI-Texte vollständig deutsch,
  gesammelte Fehlermeldung statt Dialog pro Mitglied, ICS als Ganztagstermine (aktuell 00:00-Termine).
- Wartung: `requirements.txt`, README (Python-Version, Pakete), Release_Notes (0.0.4–0.0.7), veraltete Workflow-Actions
  (`upload-artifact@v3`, `create-release@v1`), `.gitattributes` mit `eol=lf`, Duplikate in `ui/` und `model/members.py`.

## Neuer Chat — so einsteigen
1. `git status` und `git fetch` prüfen, bevor etwas geändert wird.
2. Diese Datei lesen; bei Fragen zur Struktur zuerst den Code in `model/`, `logic/`, `ui/` ansehen.
3. Bei Auswertungen (z. B. Jahr 2027): Excel-Pfad vom Nutzer erfragen, Ergebnis nur lokal ablegen, nicht committen.

## graphify

This project has a knowledge graph at graphify-out/ with god nodes, community structure, and cross-file relationships.

Rules:
- When graphify-out/graph.json exists, run `graphify query "<question>"` before your first grep, search or source-file read for a codebase question, and put this rule in every subagent prompt that explores code. Read raw files only for lines the graph or an earlier read already located. Use `graphify path "<A>" "<B>"` for relationships and `graphify explain "<concept>"` for focused concepts. These return a scoped subgraph, usually much smaller than GRAPH_REPORT.md or raw grep output.
- If graphify-out/wiki/index.md exists, use it for broad navigation instead of raw source browsing.
- Read graphify-out/GRAPH_REPORT.md only for broad architecture review or when query/path/explain do not surface enough context.
- After modifying code, run `graphify update .` to keep the graph current (AST-only, no API cost).
- A committed graphify-out/graph.json is rewritten whole on every build, so a large diff to it in a pull request is expected. Do not flag it as churn or suggest skipping the graph rebuild or its hooks.
