# Ideen für das Mitglieder Management Portal

Stand 2026-11-17. Sortiert nach Empfehlung. **Umgesetzt (committet, noch kein Release): 1, 2, 3, 4 (ohne PLZ/IBAN), 8, 9, 14, 16, 24. Umgesetzt, noch nicht committet: 26–30.** Nicht umgesetzt: 13 (Urkunden, laut Thomas noch nicht benötigt).
Ideen 31–49 (2026-11-17) sind nur notiert, **nichts davon umsetzen ohne Freigabe von Thomas**. Aufwand: S = Stunden, M = ein bis wenige Tage, L = Wochenende+.
„Beleg“ nennt, woran ich die Idee in der echten Mitgliederliste (nur Zähler) oder im Code festmache.

## Daten und Excel (Fehler an der Quelle vermeiden)

| # | Idee | Nutzen | Aufwand | Beleg / Hinweis |
|---|---|---|---|---|
| 1 | ✅ **Excel-Vorlage** mit Dropdown für „Mitglied“ (1/0), Datumsformat, Pflichtspalten farbig; Link in der App | Fehler entstehen gar nicht erst | S | In der echten Liste: 7 aktive Mitglieder mit Lücken, 7 Zellen mit Zahl statt Datum |
| 2 | ✅ **Spalten automatisch erkennen** (Nachname/Name, Geburtsdatum/Geburtstag …) statt `config.ini` | Nachfolger müssen keine Textdatei bearbeiten | M | Die `config.ini` ist die größte Hürde für Laien |
| 3 | ✅ **Einstellungen in der App** (Auswahl der Geburtstage/Jubiläen, Spaltennamen) | wie 2, ersetzt `config.ini` komplett | M | gemeinsam mit 2 umsetzen |
| 4 | ✅ **Datenprüfung erweitern:** Dubletten (Name **und** Geburtstag), Eintritt vor Geburt/weit in der Zukunft, unplausibles Alter. IBAN/PLZ bewusst nicht: die Spalte „IBAN“ enthält in der echten Liste nur Zahlen | findet Fehler, die heute niemand sieht | S–M | In der echten Liste: 2 mögliche Dubletten (Name + Vorname), evtl. Familien, daher nur als Hinweis |
| 5 | **Passwortgeschützte Excel** öffnen (Passwortabfrage) | Mitgliederlisten sind sensibel, Vereine schützen sie oft | M | `msoffcrypto-tool`; heute kommt nur „Datei nicht lesbar“ |
| 6 | **Austrittsdatum** statt nur 0/1 | Mitgliederentwicklung, Austritte pro Jahr | M | 27 von 218 Zeilen sind „Mitglied = 0“, der Zeitpunkt ist unbekannt |
| 7 | Blattauswahl, Kopfzeile nicht in Zeile 1 erkennen | robuster bei anderen Listen | S | heute wird nur das erste Blatt gelesen |

## Auswertungen

| # | Idee | Nutzen | Aufwand | Beleg / Hinweis |
|---|---|---|---|---|
| 8 | ✅ **Startseite „Demnächst“:** Geburtstage und Ehrungen der nächsten 30 Tage | Tool wird laufend nützlich, nicht nur einmal im Jahr | S | nutzt vorhandene Logik |
| 9 | ✅ **Mitgliederstatistik / Jahresbericht:** Zu- und Abgänge, Altersgruppen, Durchschnittsalter | Zahlen für Mitgliederversammlung und Verbandsmeldung | M | Altersgruppen wie Verbände sie verlangen, konfigurierbar |
| 10 | **Überfällige Ehrungen:** Jubiläen der letzten Jahre, die noch nicht geehrt wurden | nichts wird vergessen | S–M | geht heute nur über „Eigener Zeitraum“; besser mit Spalte „zuletzt geehrt“ in der Excel |
| 11 | **Beitragsklassen-Wechsel:** wer wird dieses Jahr 18 (Jugend → Erwachsene) | Beitrag stimmt automatisch | S | 18. Geburtstag ist bereits auswählbar; nur sinnvoll, wenn der Verein so abrechnet |
| 12 | Alle Geburtstage eines Monats (nicht nur runde) | Gratulationsliste für Vorstand/Presse | S | Auswahl 1.–110. statt der Liste in `config.ini` |

## Ausgabe

| # | Idee | Nutzen | Aufwand | Beleg / Hinweis |
|---|---|---|---|---|
| 13 | **Urkunden und Serienbriefe** aus Word-Vorlage (Platzhalter für Name, Jahre, Datum) | größte Zeitersparnis bei Ehrungen | M–L | `python-docx`; Vorlage vom Verein |
| 14 | ✅ **Export ohne Adresse/Telefon** (nur Name + Anlass) | datensparsam für Presse und Weitergabe (DSGVO) | S | Schalter beim Speichern |
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
| 22 | Intel-Mac-Build | mehr Geräte | M | **entschieden: nicht nötig** (2026-11-17); `macos-latest` baut nur Apple Silicon. Windows-Installer → 26 |
| 23 | Smartphone-Ansicht (Web/PWA), nur lesend: „Wer hat bald Geburtstag?“ | Excel am Handy ist heute die einzige Möglichkeit | L | Daten dürften den Rechner nur auf Wunsch verlassen |
| 24 | ✅ Windows-Build und Workflow tatsächlich auf GitHub laufen lassen | | S | Lauf für `1921be0` am 2026-11-17 grün (Windows + macOS, Tests + Smoke-Test) |
| 25 | Screenshot-Tests in CI (Offscreen-Rendern vergleichen) | Oberflächenfehler früh erkennen | M | Rendern funktioniert bereits lokal; Einstieg über 30 |

## Kostenloser Download (2026-11-17 umgesetzt, auf GitHub noch ungetestet)

Ziel: ein Link (z. B. `tomegen.github.io/member-admin`) mit je einem Knopf für Windows und Mac. Nur GitHub Releases + Pages, keine Kosten, weiterhin unsigniert (siehe 21).

| # | Idee | Nutzen | Aufwand | Beleg / Hinweis |
|---|---|---|---|---|
| 26 | ✅ **Windows-Installer** (Inno Setup): ohne Admin-Rechte in den Benutzerordner, Startmenü, Desktop-Verknüpfung, Deinstallation | Laien starten die App sonst aus dem ZIP heraus | S–M | Inno Setup im Workflow per `choco` installieren |
| 27 | ✅ **macOS-DMG** („in Programme ziehen“) | gewohnter Mac-Ablauf | S | `hdiutil` ist bei macOS dabei |
| 28 | ✅ **Feste Dateinamen ohne Version** im Release | Link `…/releases/latest/download/<Datei>` zeigt immer auf die neueste Version | S | heute steht die Version im ZIP-Namen |
| 29 | ✅ **Download-Seite** auf GitHub Pages (`docs/`): Betriebssystem erkennen, bebilderte Schritte für SmartScreen („Weitere Informationen → Trotzdem ausführen“) und Gatekeeper (macOS 15+: Systemeinstellungen → Datenschutz & Sicherheit → „Dennoch öffnen“), QR-Code zum Ausdrucken | Vorstände installieren selbst | S–M | Repo ist öffentlich, Pages daher kostenlos |
| 30 | ✅ **Windows-Screenshots in CI** (`--screenshot`-Modus, als Artefakt hochladen) | sehen, wie die App unter Windows aussieht, ohne Windows-Rechner | S | Docker scheidet aus (Mac-Docker kann keine Windows-Container, kein KVM); lokal ginge nur UTM + Windows 11 ARM. **Thomas: Docker-/VM-Test nicht nötig** |

Hinweis für die Installation vor Ort: Per USB-Stick kopiert erscheint meist keine Warnung (die Sperre greift nur bei Downloads).

## Mitglieder in der App pflegen (nur notiert, nicht umsetzen)

Würde die Festlegung „App liest nur, schreibt nie“ aufheben → vorher Thomas fragen. Vorschlag: ein **Vereinsordner** statt einer losen Excel:
`Mitglieder.xlsx` (Standardformat, weiter in Excel/am Handy bearbeitbar) · `Dateien/<Nr> <Name>/…` · `Sicherungen/…`.
Offene Fragen: Wo liegt die Excel (lokal, USB, OneDrive/Dropbox/Nextcloud)? Wie viele Vorstände ändern sie, ggf. gleichzeitig?

| # | Idee | Nutzen | Aufwand | Beleg / Hinweis |
|---|---|---|---|---|
| 31 | **Import-Assistent** (einmalig): alte Excel wählen, erkannte Spalten zeigen/korrigieren, Datenprüfung, Standard-`Mitglieder.xlsx` speichern; Original bleibt unverändert, `.xls` → `.xlsx` | einheitliches Format für alle folgenden Funktionen | M | baut auf `detect_columns` auf |
| 32 | **Standard-Schema**: Mitgliedsnummer (feste ID), bisherige Spalten, „Austritt am“, „Austrittsgrund“, „Bemerkung“, Blatt „Info“ mit Schema-Version; keine Formeln | Zeilennummern sind keine stabile ID; Formeln haben ohne Neuberechnung durch Excel keine Werte | S | |
| 33 | **Sicheres Zurückschreiben**: Sicherung vor jedem Speichern (letzte 30), Abbruch wenn Datei in Excel offen (`~$`-Sperrdatei) oder seit dem Einlesen geändert, atomar schreiben mit openpyxl (Dropdowns/Format bleiben) | keine verlorenen Änderungen bei mehreren Bearbeitern | M | Voraussetzung für 34–36 |
| 34 | **Mitglied anlegen/bearbeiten** (Formular, Datumsauswahl, Pflichtfelder, Dublettenwarnung) | Pflege ohne Excel | M | |
| 35 | **Austritt erfassen** („sunsetten“): Datum + Grund, Mitglied = 0, Person bleibt für Historie/Statistik; optional Hinweis auf Löschfristen (DSGVO) | ersetzt 6 | S | |
| 36 | **Dateien je Mitglied** (z. B. digitalisierter Mitgliedsantrag): Liste, hinzufügen per Drag & Drop, öffnen, Ordner zeigen; Ordner bleibt ohne App lesbar | Papierablage ersetzen | M | Anträge enthalten Unterschrift und SEPA-Mandat → Vereinsordner nur auf geschütztem Rechner/Cloud mit 2FA, nie in Git |

## Weitere Ideen (2026-11-17, nur notiert)

| # | Idee | Nutzen | Aufwand | Beleg / Hinweis |
|---|---|---|---|---|
| 37 | **SEPA-Lastschrift-Datei** (pain.008) für den Beitragseinzug | größte Zeitersparnis für Kassiere | M–L | braucht echte IBANs, Mandatsreferenz, Gläubiger-ID; Spalte „IBAN“ enthält heute nur Zahlen |
| 38 | **Beitragsklassen und Beitragsliste** (Jugend/Erwachsene/Familie/passiv, automatischer Wechsel nach Alter) | Beitrag stimmt automatisch | M | erweitert 11 |
| 39 | **Ehrungs-Historie** („geehrt für X Jahre am“) | macht 10 (überfällige Ehrungen) zuverlässig | S–M | |
| 40 | **Serienbrief/Einladung zur Mitgliederversammlung, Adressetiketten als PDF** | Versand ohne Word-Seriendruck | M | zusammen mit 13/15 |
| 41 | **E-Mail-Verteiler**: alle Adressen in die Zwischenablage (für BCC) | Rundmail in Sekunden | S | |
| 42 | **Mitgliedsausweis als PDF** | | S–M | |
| 43 | **Funktionen und Abteilungen** (Vorstand, Kassier, Jugend …) als Spalte und Filter | Listen je Abteilung | S–M | |
| 44 | **Familien verknüpfen** (gemeinsame Adresse, Familienbeitrag) | | M | passt zu 38 |
| 45 | **Änderungsprotokoll** als Blatt in der Excel (wer/wann/was) | Nachvollziehbarkeit bei mehreren Vorständen | S | braucht 33 |
| 46 | **DSGVO-Auskunft**: alles zu einem Mitglied (Daten + Dateien) als PDF/ZIP | Auskunftspflicht Art. 15 | S–M | braucht 36 |
| 47 | **Mitgliederentwicklung über die Jahre** als Diagramm | Jahresbericht | S | braucht 35 („Austritt am“) |
| 48 | Größe/Inhalt der **Sicherungen** anzeigen, Erinnerung an Backup | | S | braucht 33 |
| 49 | Hinweis „Neue Version verfügbar“ mit Link zur Download-Seite | | S | konkretisiert 19, braucht 28/29 |

## Meine Reihenfolge

1. ✅ 24 (Pipeline auf GitHub grün).
2. ✅ 26–30 (Installer, DMG, feste Links, Download-Seite, Windows-Screenshots). **Als Nächstes:** committen, Lauf auf GitHub prüfen, Pages aktivieren, Release 0.1.0 (nur auf Anweisung).
3. ✅ 1, 2, 3, 8, 9, 14, 16.
4. Danach, nach Rückfrage: 31–33 (Standard-Schema, Import, sicheres Schreiben) als Grundlage für 34–36 und 45–48.
5. 13 (Urkunden): größter Nutzen bei Ehrungen, braucht eine Vorlage vom Verein; zurückgestellt.
6. Offen und klein: 10/39 (überfällige Ehrungen), 12, 17 (Hilfe), 18, 20, 41.
