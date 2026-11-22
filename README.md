# Mitglieder Management Portal

Ein kostenloses Programm für Vereinsvorstände: **Mitglieder pflegen**, **runde Geburtstage** und **Ehrungen für
langjährige Mitgliedschaft** berechnen, eine **Mitgliederstatistik** erstellen – mit einer ganz normalen
Excel-Datei als Mitgliederliste.

Die Excel-Datei bleibt der Datenspeicher: Sie kann in Dropbox, OneDrive/SharePoint, Google Drive oder Nextcloud
liegen, im Vorstand geteilt und auch **ohne das Programm** bearbeitet werden, z. B. am Smartphone. Das Programm
sendet keine Daten ins Internet.

## Installation

**Download-Seite mit Schritt-für-Schritt-Anleitung: [tomegen.github.io/member-admin](https://tomegen.github.io/member-admin/)**

| System | Datei (unter [Releases](../../releases)) | Installieren |
|---|---|---|
| Windows 10/11 | `Mitgliederverwaltung-Windows-Setup.exe` | öffnen, „Installieren“ (keine Administratorrechte nötig); danach auf dem Desktop und im Startmenü |
| Windows ohne Installation | `Mitgliederverwaltung-Windows.zip` | entpacken, `Mitgliederverwaltung.exe` doppelklicken |
| Mac (Apple-Chip, ab Ende 2020) | `Mitgliederverwaltung-Mac.dmg` | öffnen, `Mitgliederverwaltung` auf „Programme“ ziehen |

Eine neue Version installieren Sie genauso. Ihre Mitgliederliste und deren Einstellungen bleiben unverändert.

**Warum erscheint beim ersten Start eine Warnung?** Das Programm ist (noch) nicht bei Microsoft bzw. Apple
registriert; das kostet jährlich Geld. Das Programm ist trotzdem unbedenklich, der Quellcode ist öffentlich.
- **Windows:** „Weitere Informationen“ → „Trotzdem ausführen“.
- **Mac:** Wenn macOS das Öffnen verweigert: *Systemeinstellungen → Datenschutz & Sicherheit*, nach unten scrollen
  und bei der Meldung zu „Mitgliederverwaltung“ auf **„Dennoch öffnen“** klicken. Ab dann startet die App normal.
  (Bei älteren macOS-Versionen geht auch: Rechtsklick auf die App → „Öffnen“.)

Die Datei `config.ini` neben dem Programm (Windows) ist **optional** (nur für Fortgeschrittene, siehe unten).

## So geht es

1. Programm starten und **„Mitgliederliste öffnen“** (oder die Datei in das Fenster ziehen). Beim nächsten Start
   bietet das Programm die zuletzt benutzte Datei direkt an.
   - **Noch keine Liste?** „Neue leere Mitgliederliste anlegen“.
   - **Bisherige Liste aus Excel oder einem anderen Programm?** Einfach öffnen: Der **Import-Assistent** übernimmt sie
     in eine neue Datei im Format des Programms (siehe unten). Die bisherige Liste bleibt unverändert.
2. Oben das **Auswertungsjahr** prüfen. Ab Oktober schlägt das Programm automatisch das nächste Jahr vor.
3. Auf der **Übersicht** steht unter „Demnächst“, wer in den nächsten 30 Tagen Geburtstag oder Jubiläum hat.
4. Im Tab **Mitglieder** suchen, neue Mitglieder anlegen, bearbeiten (Doppelklick) und **Austritte erfassen**.
   Gespeichert wird direkt in der Mitgliederliste.
5. Im Tab **Geburtstage** oder **Ehrungen** sehen Sie sofort die Treffer, mit dem Geschenk, das der Verein dafür
   vorsieht. Wer nicht ein ganzes Jahr braucht, wählt „Eigener Zeitraum“. Speichern als **Textdatei, Excel-Datei oder
   Kalender (ICS)** – die Kalenderdatei lässt sich in Outlook, Apple Kalender oder Google Kalender importieren
   (Ganztagstermine, auf Wunsch mit Erinnerung). Mit **„Nur Name und Anlass“** enthält die Datei weder Geburtstag
   noch Telefon, Adresse oder Geschenk – praktisch für die Presse.
6. Der Tab **Statistik** zeigt Mitglieder (davon passiv), Neue, Altersgruppen (wie bei Verbandsmeldungen) und das
   Durchschnittsalter; als Excel-Datei speicherbar.
7. Der Tab **Datenprüfung** zeigt unvollständige oder auffällige Einträge (fehlende Angaben, unmögliches Alter,
   Eintritt vor der Geburt, doppelte Einträge oder Nummern) mit der **Zeilennummer aus Excel**.

## Die Mitgliederliste (Excel-Datei)

Die Datei hat mehrere Blätter. Bearbeiten Sie sie im Programm oder direkt in Excel, Google Tabellen oder am Handy –
das Programm liest Änderungen automatisch neu ein.

| Blatt | Inhalt |
|---|---|
| **Mitglieder** | eine Zeile pro Person. Blau = Pflicht: Name, Vorname, Geschlecht, Geburtstag, Eintritt, Status. Dazu Nr, Austritt am/-grund, Abteilung, Beitragsklasse, Anschrift, Telefon, Mobil, E-Mail, IBAN, Mandatsreferenz, Bemerkung. |
| **Funktionen** | Ämter mit Nr des Mitglieds, Funktion, von, bis |
| **Einstellungen** | welche Geburtstage und Jubiläen gefeiert werden und mit welchem Geschenk; Auswahllisten (Abteilungen, Beitragsklassen, Funktionen); Vereinsname, Löschfrist, Kalender-Erinnerung, ob passive Mitglieder mitzählen |
| **Änderungsprotokoll** | wer wann was im Programm geändert hat (Änderungen direkt in Excel stehen hier nicht) |
| **Info** | Kurzanleitung für die Pflege von Hand; nicht löschen |

Pflege von Hand – das Wichtigste (steht auch im Blatt „Info“):
- **Nr** bei neuen Mitgliedern leer lassen; das Programm vergibt sie („Nummern vergeben“). Nummern nie ändern.
- **Austritt:** Status „ausgetreten“ und „Austritt am“ eintragen, die Zeile **nicht löschen**.
- Spalten dürfen verschoben und eigene Spalten ergänzt werden; die Überschriften der Pflichtspalten bitte nicht ändern.

## Liste übernehmen (Import) und abgleichen

Jede Liste, die nicht im Format des Programms ist (`.xlsx`, `.xls`, `.csv`, z. B. aus anderer Vereinssoftware),
öffnet den **Import-Assistenten**: Das Programm findet die Überschriften (auch unter einer Titelzeile), schlägt vor,
welche Spalte zu welchem Feld gehört, trennt „Müller, Hans“ und „12345 Musterstadt“ und übersetzt Einträge wie
„x“/„ja“/„0“ oder „Herr“/„Frau“. Fehlende Angaben tragen Sie im Assistenten nach, auch für viele Zeilen auf einmal.
Fehlt das Geschlecht, schätzt das Programm es aus dem Vornamen – Sie bestätigen das. **Unbekannte Daten**
(Geburtstag, Eintritt, Austrittsdatum) dürfen leer bleiben: Die Datenprüfung zeigt sie, bis Sie sie ergänzen. Wer
keinen Geburtstag hat, fehlt nur bei den Geburtstagen und in den Altersgruppen; ohne Eintritt fehlt er bei den
Ehrungen; ohne Austrittsdatum greift für ihn die Löschfrist nicht (Löschen von Hand geht).

Später kommen neue Daten dazu (z. B. ein Export des Verbands oder eine Liste mit E-Mail-Adressen)? Im Tab
**Mitglieder → Weitere … → „Liste abgleichen“**: Das Programm zeigt neue Personen und jede Änderung einzeln, Sie
haken an, was übernommen wird. Leere Werte der Liste löschen nie etwas.

## Gemeinsam nutzen und Sicherheit

- **Vor jedem Speichern** legt das Programm eine Sicherung im Ordner **`Sicherungen`** neben der Datei an
  (die letzten 30 und eine pro Monat für ein Jahr).
- Hat jemand anderes die Datei inzwischen geändert (z. B. am Handy), bleiben seine Änderungen erhalten. Nur wenn
  beide **dasselbe Feld** geändert haben, fragt das Programm, welcher Wert gilt.
- Ist die Datei gerade in Excel geöffnet, wartet das Programm mit dem Speichern.
- Speichern zwei Personen gleichzeitig, legt der Cloud-Dienst manchmal eine **Konfliktkopie** an. Das Programm
  erkennt sie, zeigt die Unterschiede und räumt sie danach in den Ordner „Sicherungen“.
- **Löschfrist:** Im Blatt „Einstellungen“ (oder im Programm unter **Einstellungen**) kann der Verein festlegen, nach
  wie vielen Jahren Ausgetretene endgültig gelöscht werden. Das Programm weist darauf hin; gelöscht wird nur nach
  Bestätigung. Standard: nie.
- Die Datei enthält personenbezogene Daten: Teilen Sie sie nur im Vorstand und nutzen Sie beim Cloud-Dienst eine
  Zwei-Faktor-Anmeldung.

## Regeln der Berechnung

- Es zählen aktive Mitglieder; passive Mitglieder, wenn der Verein es in den Einstellungen so festlegt (Standard: ja).
  Ausgetretene zählen nicht.
- **Geburtstag:** Wer im gewählten Zeitraum z. B. seinen 60. Geburtstag hat. Wer am **29. Februar** geboren ist, feiert in
  Jahren ohne Schalttag am **28. Februar**.
- **Ehrung:** Wer im gewählten Zeitraum z. B. 25 Jahre Mitglied wird (Eintritt plus Jahre).
- Fehlt der Geburtstag oder der Eintritt, erscheint die Person in der Datenprüfung und in der jeweiligen Auswertung nicht.

## Einstellungen

Die Einstellungen des Vereins stehen in der Mitgliederliste selbst (Blatt „Einstellungen“) und gelten für alle, die
sie nutzen. Im Programm: Knopf **Einstellungen**. Nur auf Ihrem Computer gespeichert wird Ihr Name für das
Änderungsprotokoll.

Für Fortgeschrittene gibt es die optionale Textdatei `config.ini` (neben dem Programm): Standardwerte für die
Geburtstage/Jubiläen neuer Listen und bevorzugte Spaltennamen für den Import.

---

## Für Entwickler

Python 3.12, [PySide6](https://doc.qt.io/qtforpython-6/) (Oberfläche), pandas/openpyxl/xlrd (Excel), icalendar.
Aufbau und Festlegungen: `CLAUDE.md`, Konzept der Datenhaltung: `PLAN_DATA_STORAGE.md`.

```bash
uv venv --python 3.12 .venv
uv pip install --python .venv/bin/python -r requirements-dev.txt   # Windows: .venv\Scripts\python.exe
.venv/bin/python mitgliederverwaltung.py [mitgliederliste.xlsx]
for t in regressions ui store import; do .venv/bin/python tests/test_$t.py; done
.venv/bin/python build.py 0.2.0        # Mac: release/Mitgliederverwaltung-Mac.dmg; Windows: -Windows-Setup.exe (mit Inno Setup 6) und -Windows.zip
```

- **Release:** GitHub → Actions → „Build and Release“ → *Run workflow* mit Versionsnummer (z. B. `0.1.0`). Der Workflow
  testet, baut Windows-Installer und Mac-DMG, installiert und prüft sie (`--smoke-test`) und legt das Release an.
  Bei jedem Push auf `main` laufen nur Tests und Build. Screenshots aller Tabs (Windows und Mac, mit der Beispieldatei)
  liegen beim jeweiligen Lauf unter *Artifacts* (`--screenshots=<ordner>`).
- **Download-Seite:** `docs/index.html` über GitHub Pages (Settings → Pages → *Deploy from a branch* → `main` / `/docs`).
  Sie verlinkt `releases/latest/download/<Dateiname>`; die Dateinamen enthalten deshalb keine Versionsnummer.
- Details für die Weiterentwicklung (auch mit Claude Code): `CLAUDE.md`.
- Echte Mitgliederlisten gehören nie ins Repository (`data/` und `*.xlsx` sind ignoriert).
