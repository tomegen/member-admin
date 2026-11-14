# Ideen für das Mitglieder Management Portal

Stand 2026-11-14. Sortiert nach Empfehlung. Aufwand: S = Stunden, M = ein bis wenige Tage, L = Wochenende+.
„Beleg“ nennt, woran ich die Idee in der echten Mitgliederliste (nur Zähler) oder im Code festmache.

## Daten und Excel (Fehler an der Quelle vermeiden)

| # | Idee | Nutzen | Aufwand | Beleg / Hinweis |
|---|---|---|---|---|
| 1 | **Excel-Vorlage** mit Dropdown für „Mitglied“ (1/0), Datumsformat, Pflichtspalten farbig; Link in der App | Fehler entstehen gar nicht erst | S | In der echten Liste: 7 aktive Mitglieder mit Lücken, 7 Zellen mit Zahl statt Datum |
| 2 | **Spalten automatisch erkennen** (Nachname/Name, Geburtsdatum/Geburtstag …) statt `config.ini` | Nachfolger müssen keine Textdatei bearbeiten | M | Die `config.ini` ist die größte Hürde für Laien |
| 3 | **Einstellungen in der App** (Auswahl der Geburtstage/Jubiläen, Spaltennamen) | wie 2, ersetzt `config.ini` komplett | M | gemeinsam mit 2 umsetzen |
| 4 | **Datenprüfung erweitern:** Dubletten, Eintritt vor Geburt/in der Zukunft, unplausibles Alter, PLZ/IBAN-Format | findet Fehler, die heute niemand sieht | S–M | In der echten Liste: 2 mögliche Dubletten (Name + Vorname), evtl. Familien, daher nur als Hinweis |
| 5 | **Passwortgeschützte Excel** öffnen (Passwortabfrage) | Mitgliederlisten sind sensibel, Vereine schützen sie oft | M | `msoffcrypto-tool`; heute kommt nur „Datei nicht lesbar“ |
| 6 | **Austrittsdatum** statt nur 0/1 | Mitgliederentwicklung, Austritte pro Jahr | M | 27 von 218 Zeilen sind „Mitglied = 0“, der Zeitpunkt ist unbekannt |
| 7 | Blattauswahl, Kopfzeile nicht in Zeile 1 erkennen | robuster bei anderen Listen | S | heute wird nur das erste Blatt gelesen |

## Auswertungen

| # | Idee | Nutzen | Aufwand | Beleg / Hinweis |
|---|---|---|---|---|
| 8 | **Startseite „Demnächst“:** Geburtstage und Ehrungen der nächsten 30 Tage | Tool wird laufend nützlich, nicht nur einmal im Jahr | S | nutzt vorhandene Logik |
| 9 | **Mitgliederstatistik / Jahresbericht:** Zu- und Abgänge, Altersgruppen, Durchschnittsalter | Zahlen für Mitgliederversammlung und Verbandsmeldung | M | Altersgruppen wie Verbände sie verlangen, konfigurierbar |
| 10 | **Überfällige Ehrungen:** Jubiläen der letzten Jahre, die noch nicht geehrt wurden | nichts wird vergessen | S–M | geht heute nur über „Eigener Zeitraum“; besser mit Spalte „zuletzt geehrt“ in der Excel |
| 11 | **Beitragsklassen-Wechsel:** wer wird dieses Jahr 18 (Jugend → Erwachsene) | Beitrag stimmt automatisch | S | 18. Geburtstag ist bereits auswählbar; nur sinnvoll, wenn der Verein so abrechnet |
| 12 | Alle Geburtstage eines Monats (nicht nur runde) | Gratulationsliste für Vorstand/Presse | S | Auswahl 1.–110. statt der Liste in `config.ini` |

## Ausgabe

| # | Idee | Nutzen | Aufwand | Beleg / Hinweis |
|---|---|---|---|---|
| 13 | **Urkunden und Serienbriefe** aus Word-Vorlage (Platzhalter für Name, Jahre, Datum) | größte Zeitersparnis bei Ehrungen | M–L | `python-docx`; Vorlage vom Verein |
| 14 | **Export ohne Adresse/Telefon** (nur Name + Anlass) | datensparsam für Presse und Weitergabe (DSGVO) | S | Schalter beim Speichern |
| 15 | **Schöne PDF-Liste** für die Vorstandssitzung | statt TXT/Excel direkt druckbar | M | Qt kann PDF drucken |
| 16 | ICS mit **Erinnerung** (z. B. 1 Woche vorher) und ICS auch für Ehrungen | Termine werden nicht verpasst | S | `VALARM` im Kalender-Export |

## Bedienung und Betrieb

| # | Idee | Nutzen | Aufwand | Beleg / Hinweis |
|---|---|---|---|---|
| 17 | Hilfe-Menü, Tooltips, 1-seitige Kurzanleitung (PDF) | weniger Rückfragen an Thomas | S | README ist da, aber nicht in der App |
| 18 | Größere Schrift / Dunkelmodus einstellbar | ältere Vorstände | S | Qt bringt das fast mit |
| 19 | Hinweis „Neue Version verfügbar“ | Nachfolger bleiben aktuell | M | braucht Netzwerk, daher nur optional und abschaltbar; widerspricht „bleibt offline“ |
| 20 | Knopf „Problem melden“ (Diagnose ohne Personendaten in die Zwischenablage) | Support ohne Fernzugriff | S | |

## Verteilung und Technik (zurückgestellt oder offen)

| # | Idee | Nutzen | Aufwand | Beleg / Hinweis |
|---|---|---|---|---|
| 21 | Signierung/Notarisierung (Apple Developer ID, Windows) | keine Warnung beim Start | M + Kosten | **entschieden: vorerst nicht** (2026-11-14) |
| 22 | Intel-Mac-Build, Windows-Installer | mehr Geräte, einfacher zu installieren | M | `macos-latest` baut nur Apple Silicon |
| 23 | Smartphone-Ansicht (Web/PWA), nur lesend: „Wer hat bald Geburtstag?“ | Excel am Handy ist heute die einzige Möglichkeit | L | Daten dürften den Rechner nur auf Wunsch verlassen |
| 24 | Windows-Build und Workflow tatsächlich auf GitHub laufen lassen | derzeit ungetestet | S | erster Schritt vor dem nächsten Release |
| 25 | Screenshot-Tests in CI (Offscreen-Rendern vergleichen) | Oberflächenfehler früh erkennen | M | Rendern funktioniert bereits lokal |

## Meine Reihenfolge

1. 24 (Pipeline prüfen), dann ein erstes Release.
2. 1, 2, 3 (Vorlage, Spalten erkennen, Einstellungen in der App): macht das Tool für Nachfolger wirklich einfach.
3. 8, 9, 16, 14: schnelle Gewinne.
4. 13 (Urkunden): größter Nutzen bei Ehrungen, braucht eine Vorlage vom Verein.
