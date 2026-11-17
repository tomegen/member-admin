# Mitglieder Management Portal

Berechnet aus Ihrer Mitgliederliste (Excel) automatisch **runde Geburtstage** und **Ehrungen für langjährige
Mitgliedschaft** – für ein Jahr oder einen beliebigen Zeitraum. Das Ergebnis können Sie als Text, als Excel-Datei
oder als Kalenderdatei speichern. Dazu gibt es eine Übersicht „Demnächst“ und eine Mitgliederstatistik.

Ihre Daten bleiben auf Ihrem Computer. Die Mitgliederliste wird nur gelesen und nie verändert.

## Installation

Laden Sie unter [Releases](../../releases) die Datei für Ihr System herunter und entpacken Sie sie:

| System | Datei | Starten |
|---|---|---|
| Windows | `Mitgliederverwaltung_<Version>_windows.zip` | Ordner entpacken, `Mitgliederverwaltung.exe` doppelklicken |
| Mac (Apple Silicon, ab 2020) | `Mitgliederverwaltung_<Version>_mac.zip` | entpacken, `Mitgliederverwaltung.app` doppelklicken |

**Warum erscheint beim ersten Start eine Warnung?** Das Programm ist (noch) nicht bei Microsoft bzw. Apple
registriert; das kostet jährlich Geld. Das Programm ist trotzdem unbedenklich, der Quellcode ist öffentlich.
- **Windows:** „Weitere Informationen“ → „Trotzdem ausführen“.
- **Mac:** Wenn macOS das Öffnen verweigert: *Systemeinstellungen → Datenschutz & Sicherheit*, nach unten scrollen
  und bei der Meldung zu „Mitgliederverwaltung“ auf **„Trotzdem öffnen“** klicken. Ab dann startet die App normal.
  (Bei älteren macOS-Versionen geht auch: Rechtsklick auf die App → „Öffnen“.)

Die Datei `config.ini` neben dem Programm ist **optional** (nur für Fortgeschrittene, siehe unten).

## So geht es

1. Programm starten und die **Excel-Mitgliederliste auswählen** (oder die Datei in das Fenster ziehen).
   Beim nächsten Start bietet das Programm die zuletzt benutzte Datei direkt an.
2. Oben das **Auswertungsjahr** prüfen. Ab Oktober schlägt das Programm automatisch das nächste Jahr vor.
3. Auf der **Übersicht** steht unter „Demnächst“, wer in den nächsten 30 Tagen Geburtstag oder Jubiläum hat.
4. Im Tab **Geburtstage** oder **Ehrungen** sehen Sie sofort die Treffer. Mit den Häkchen wählen Sie, welche
   Geburtstage bzw. Jubiläen berücksichtigt werden. Wer nicht ein ganzes Jahr braucht, wählt „Eigener Zeitraum“.
   Welche Zahlen zur Auswahl stehen, ändern Sie oben unter **Einstellungen**.
5. Mit **Als Textdatei / Excel-Datei / Kalender (ICS) speichern** erzeugen Sie die Liste. Die Kalenderdatei
   lässt sich in Outlook, Apple Kalender oder Google Kalender importieren (Ganztagstermine, auf Wunsch mit Erinnerung).
   Mit dem Häkchen **Nur Name und Anlass** enthält die Datei weder Geburtstag noch Telefon oder Adresse –
   praktisch für die Presse oder zur Weitergabe.
6. Der Tab **Statistik** zeigt aktive Mitglieder, Neue, Altersgruppen (wie bei Verbandsmeldungen) und das Durchschnittsalter.
   Die Zahlen lassen sich als Excel-Datei speichern.
7. Im Tab **Datenprüfung** steht, welche Einträge in Ihrer Liste unvollständig oder auffällig sind (fehlende Daten, unmögliches
   Alter, Eintritt vor der Geburt, doppelte Einträge) – mit der **Zeilennummer aus Excel**. Fehlende Angaben führen dazu,
   dass Personen in den Auswertungen fehlen. Korrigieren Sie sie in Excel, speichern Sie und klicken Sie
   oben auf **Neu einlesen**.

## Die Excel-Liste

In der ersten Zeile stehen die Spaltenüberschriften, darunter je Zeile ein Mitglied. Die Beispieldatei
`example_file.xlsx` zeigt den Aufbau. Die Spalten dürfen in beliebiger Reihenfolge stehen, weitere Spalten werden ignoriert.
Das Programm erkennt die Spalten an der Überschrift, auch bei üblichen anderen Schreibweisen (z. B. „Nachname“,
„Geburtsdatum“, „Eintritt“, „Aktiv“, „Handy“).

**Noch keine Liste?** Auf der Startseite gibt es **„Leere Excel-Vorlage speichern“**: mit Auswahlfeld für „Mitglied“
(1/0), Datumsprüfung und farblich markierten Pflichtspalten.

| Spalte | Pflicht? | Hinweis |
|---|---|---|
| Name, Vorname | ja | |
| Geburtstag | ja | als Excel-Datum |
| Mitglied seit | ja | als Excel-Datum |
| Mitglied | ja | `1` = aktives Mitglied, `0` = ausgetreten/nicht zählend (Zeile bitte nicht löschen, auf `0` setzen) |
| Strasse, Plz, Ort, Telefon, Mobil, IBAN, Mandatreferenz | nein | Telefon, Anschrift erscheinen in den Ergebnislisten |

Leere Zeilen werden übersprungen. Ob die Liste nur am PC oder auch auf dem Smartphone gepflegt wird, spielt keine Rolle.

## Regeln der Berechnung

- Es zählen nur Mitglieder mit `Mitglied = 1`.
- **Geburtstag:** Wer im gewählten Zeitraum z. B. seinen 60. Geburtstag hat. Wer am **29. Februar** geboren ist, feiert in
  Jahren ohne Schalttag am **28. Februar**.
- **Ehrung:** Wer im gewählten Zeitraum z. B. 25 Jahre Mitglied wird (Datum „Mitglied seit“ plus Jahre).
- Fehlt der Geburtstag oder „Mitglied seit“, erscheint die Person in der Datenprüfung und in der jeweiligen Auswertung nicht.

## Einstellungen

Unter **Einstellungen** (oben im Programm) legen Sie fest, welche Geburtstage und Jubiläumsjahre zur Auswahl stehen.
Die Auswahl wird gespeichert; „Standard wiederherstellen“ setzt sie zurück.

Für Fortgeschrittene gibt es die optionale Textdatei `config.ini` (neben dem Programm):
- `[birthday] possibilities` und `[honor] possibilities`: Standardwerte für die Auswahl.
- `[excel_columns]`: bevorzugter Spaltenname. Das Programm erkennt Spalten auch ohne diese Datei; sie hilft nur, wenn
  Ihre Überschrift ungewöhnlich heißt.

---

## Für Entwickler

Python 3.12, [PySide6](https://doc.qt.io/qtforpython-6/) (Oberfläche), pandas/openpyxl/xlrd (Excel), icalendar.

```bash
uv venv --python 3.12 .venv
uv pip install --python .venv/bin/python -r requirements-dev.txt   # Windows: .venv\Scripts\python.exe
.venv/bin/python mitgliederverwaltung.py [mitgliederliste.xlsx]
.venv/bin/python tests/test_regressions.py && .venv/bin/python tests/test_ui.py
.venv/bin/python build.py 0.1.0        # erzeugt release/Mitgliederverwaltung_0.1.0_<system>.zip
```

- **Release:** GitHub → Actions → „Build and Release“ → *Run workflow* mit Versionsnummer (z. B. `0.1.0`). Der Workflow
  testet, baut Windows- und Mac-Version, prüft die gepackten Apps (`--smoke-test`) und legt das Release an.
  Bei jedem Push auf `main` laufen nur Tests und Build.
- Details für die Weiterentwicklung (auch mit Claude Code): `CLAUDE.md`.
- Echte Mitgliederlisten gehören nie ins Repository (`data/` und `*.xlsx` sind ignoriert).
