# Graph Report - member-admin  (2026-11-19)

## Corpus Check
- 38 files · ~20,771 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 5 file(s) not represented in the graph (top: (none) 2, .ini 1, .iss 1)

## Summary
- 446 nodes · 1089 edges · 24 communities (18 shown, 6 thin omitted)
- Extraction: 91% EXTRACTED · 9% INFERRED · 0% AMBIGUOUS · INFERRED: 93 edges (avg confidence: 0.9)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `efac6fa7`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- with
- club_file.py
- birthday_calculation.py
- main_window.py
- build.py
- MainWindow
- detect_columns
- Release_Notes.md
- Mitglieder Management Portal
- .claude/CLAUDE.md
- Members
- ResultPage
- StatisticsPage
- release
- steps
- version
- mitgliederverwaltung.py
- build
- strategy
- Member
- template.py
- StandardFileTest

## God Nodes (most connected - your core abstractions)
1. `Members` - 39 edges
2. `MainWindow` - 32 edges
3. `make_member()` - 20 edges
4. `MemberListTest` - 20 edges
5. `Config` - 20 edges
6. `ResultPage` - 19 edges
7. `UiTest` - 19 edges
8. `Member` - 16 edges
9. `StandardFileTest` - 16 edges
10. `Aufbau` - 16 edges

## Surprising Connections (you probably didn't know these)
- `7. Tests` --references--> `is_standard()`  [INFERRED]
  PLAN_DATA_STORAGE.md → model/club_file.py
- `Aufbau` --references--> `age_on()`  [INFERRED]
  CLAUDE.md → model/checks.py
- `6. Code` --references--> `is_standard()`  [INFERRED]
  PLAN_DATA_STORAGE.md → model/club_file.py
- `Aufbau` --references--> `Member`  [INFERRED]
  CLAUDE.md → model/member.py
- `Stand der Umsetzung` --references--> `Members`  [INFERRED]
  PLAN_DATA_STORAGE.md → model/members.py

## Import Cycles
- None detected.

## Communities (24 total, 6 thin omitted)

### Community 0 - "with"
Cohesion: 0.18
Nodes (11): with, cache, cache-dependency-path, files, if-no-files-found, merge-multiple, name, path (+3 more)

### Community 1 - "club_file.py"
Cohesion: 0.09
Nodes (29): Aufbau, CLAUDE.md — member-admin ("Mitglieder Management Portal"), Entwickeln (macOS/Windows), Festlegungen (nicht rückgängig machen), graphify, Neuer Chat — so einsteigen, Regeln für Änderungen, Verteilung / offene Punkte (Stand 2026-11-17) (+21 more)

### Community 2 - "birthday_calculation.py"
Cohesion: 0.09
Nodes (24): find_birthdays(), is_birthday(), write_birthdays_into_ics(), write_birthdays_into_txt(), reminder(), write_entries_into_ics(), shift_years(), entries_to_rows() (+16 more)

### Community 3 - "main_window.py"
Cohesion: 0.11
Nodes (15): parse_numbers(), IssuesPage, NumberItem, default_year(), make_card(), OverviewPage, save_file(), as_text() (+7 more)

### Community 4 - "build.py"
Cohesion: 0.38
Nodes (4): find_inno_setup(), package(), package_mac(), package_windows()

### Community 6 - "detect_columns"
Cohesion: 0.12
Nodes (13): Ausgabe, Auswertungen, Bedienung und Betrieb, Daten und Excel (Fehler an der Quelle vermeiden), Ideen für das Mitglieder Management Portal, Kostenloser Download (2026-11-17 umgesetzt, live: tomegen.github.io/member-admin), Meine Reihenfolge, Mitglieder in der App pflegen (nur notiert, nicht umsetzen) (+5 more)

### Community 7 - "Release_Notes.md"
Cohesion: 0.33
Nodes (5): Version 0.0.1, Version 0.0.2, Version 0.0.3, Version 0.1.0, Versionen 0.0.4 – 0.0.7

### Community 8 - "Mitglieder Management Portal"
Cohesion: 0.25
Nodes (7): Die Excel-Liste, Einstellungen, Für Entwickler, Installation, Mitglieder Management Portal, Regeln der Berechnung, So geht es

### Community 10 - "Members"
Cohesion: 0.16
Nodes (3): Members, DataCheckTest, MemberListTest

### Community 12 - "StatisticsPage"
Cohesion: 0.17
Nodes (7): age_group_label(), Statistics, age_on(), plausibility_issues(), StatisticsTest, german_number(), StatisticsPage

### Community 14 - "release"
Cohesion: 0.22
Nodes (9): jobs, release, name, permissions, contents, if, needs, permissions (+1 more)

### Community 15 - "steps"
Cohesion: 0.25
Nodes (9): steps, steps, continue-on-error, if, name, run, shell, timeout-minutes (+1 more)

### Community 16 - "version"
Cohesion: 0.22
Nodes (9): version, on, push, workflow_dispatch, branches, description, required, type (+1 more)

### Community 17 - "mitgliederverwaltung.py"
Cohesion: 0.12
Nodes (8): Config, ConfigError, write_statistics_into_xlsx(), main(), smoke_test(), take_screenshots(), SettingsTest, apply_theme()

### Community 18 - "build"
Cohesion: 0.33
Nodes (6): env, runs-on, timeout-minutes, QT_QPA_PLATFORM, build, env

### Community 19 - "strategy"
Cohesion: 0.33
Nodes (6): strategy, name, os, include, fail-fast, matrix

### Community 20 - "Member"
Cohesion: 0.10
Nodes (20): Member, 10. Geklärte Detailpunkte (2026-11-19), 1. Dateiformat (Schema-Version 1), 2. Sicheres Speichern, 3. Konfliktkopien, 5. Oberfläche, 6. Code, 7. Tests (+12 more)

### Community 21 - "template.py"
Cohesion: 0.20
Nodes (13): add_check(), check_for(), date_check(), list_check(), number_check(), write_functions_sheet(), write_headings(), write_info_sheet() (+5 more)

## Knowledge Gaps
- **6 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Members` connect `Members` to `club_file.py`, `birthday_calculation.py`, `main_window.py`, `MainWindow`, `mitgliederverwaltung.py`, `Member`, `template.py`, `StandardFileTest`?**
  _High betweenness centrality (0.133) - this node is a cross-community bridge._
- **Are the 7 inferred relationships involving `Members` (e.g. with `Member` and `Stand der Umsetzung`) actually correct?**
  _`Members` has 7 INFERRED edges - model-reasoned connections that need verification._
- **Should `club_file.py` be split into smaller, more focused modules?**
  _Cohesion score 0.08865248226950355 - nodes in this community are weakly interconnected._
- **Why does `MainWindow` connect `MainWindow` to `club_file.py`, `birthday_calculation.py`, `main_window.py`, `Members`, `ResultPage`, `StatisticsPage`, `mitgliederverwaltung.py`?**
  _High betweenness centrality (0.078) - this node is a cross-community bridge._
- **Are the 9 inferred relationships involving `MainWindow` (e.g. with `MemberListError` and `Members`) actually correct?**
  _`MainWindow` has 9 INFERRED edges - model-reasoned connections that need verification._
- **Should `birthday_calculation.py` be split into smaller, more focused modules?**
  _Cohesion score 0.08717948717948718 - nodes in this community are weakly interconnected._
- **Why does `detect_columns()` connect `detect_columns` to `club_file.py`, `birthday_calculation.py`?**
  _High betweenness centrality (0.065) - this node is a cross-community bridge._