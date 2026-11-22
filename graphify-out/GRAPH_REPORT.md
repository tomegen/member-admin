# Graph Report - member-admin  (2026-11-22)

## Corpus Check
- 45 files · ~24,400 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 5 file(s) not represented in the graph (top: (none) 2, .ini 1, .iss 1)

## Summary
- 544 nodes · 1480 edges · 24 communities (18 shown, 6 thin omitted)
- Extraction: 92% EXTRACTED · 8% INFERRED · 0% AMBIGUOUS · INFERRED: 113 edges (avg confidence: 0.9)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `cabf3699`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- with
- club_file.py
- birthday_calculation.py
- main_window.py
- os
- MainWindow
- detect_columns
- Release_Notes.md
- Mitglieder Management Portal
- .claude/CLAUDE.md
- Members
- ResultPage
- test_store.py
- release
- steps
- version
- CLAUDE.md — member-admin ("Mitglieder Management Portal")
- build
- strategy
- Member
- template.py
- StandardFileTest

## God Nodes (most connected - your core abstractions)
1. `Members` - 41 edges
2. `save()` - 34 edges
3. `MainWindow` - 32 edges
4. `Aufbau` - 23 edges
5. `Config` - 22 edges
6. `MemberListTest` - 20 edges
7. `make_member()` - 20 edges
8. `update_member()` - 19 edges
9. `ResultPage` - 19 edges
10. `UiTest` - 19 edges

## Surprising Connections (you probably didn't know these)
- `7. Tests` --references--> `is_standard()`  [INFERRED]
  PLAN_DATA_STORAGE.md → model/club_file.py
- `4. Import-Assistent (QWizard)` --references--> `detect_columns()`  [INFERRED]
  PLAN_DATA_STORAGE.md → model/columns.py
- `Mitglieder in der App pflegen (nur notiert, nicht umsetzen)` --references--> `detect_columns()`  [INFERRED]
  IDEAS.md → model/columns.py
- `6. Code` --references--> `is_standard()`  [INFERRED]
  PLAN_DATA_STORAGE.md → model/club_file.py
- `Aufbau` --references--> `is_standard_file()`  [INFERRED]
  CLAUDE.md → model/club_file.py

## Import Cycles
- None detected.

## Communities (24 total, 6 thin omitted)

### Community 0 - "with"
Cohesion: 0.18
Nodes (11): with, cache, cache-dependency-path, files, if-no-files-found, merge-multiple, name, path (+3 more)

### Community 1 - "club_file.py"
Cohesion: 0.08
Nodes (25): cell_key(), choice(), file_hash(), headings(), is_standard(), is_standard_file(), members_sheet(), MissingColumns (+17 more)

### Community 2 - "birthday_calculation.py"
Cohesion: 0.08
Nodes (30): Festlegungen (nicht rückgängig machen), find_birthdays(), is_birthday(), write_birthdays_into_ics(), write_birthdays_into_txt(), reminder(), write_entries_into_ics(), shift_years() (+22 more)

### Community 3 - "main_window.py"
Cohesion: 0.06
Nodes (26): ConfigError, parse_numbers(), Statistics, write_statistics_into_xlsx(), main(), smoke_test(), take_screenshots(), StatisticsTest (+18 more)

### Community 4 - "os"
Cohesion: 0.19
Nodes (9): find_inno_setup(), package(), package_mac(), package_windows(), backup_folder(), backups_of(), rotate(), write_backup() (+1 more)

### Community 6 - "detect_columns"
Cohesion: 0.18
Nodes (10): Ausgabe, Auswertungen, Bedienung und Betrieb, Daten und Excel (Fehler an der Quelle vermeiden), Ideen für das Mitglieder Management Portal, Kostenloser Download (2026-11-17 umgesetzt, live: tomegen.github.io/member-admin), Meine Reihenfolge, Mitglieder in der App pflegen (nur notiert, nicht umsetzen) (+2 more)

### Community 7 - "Release_Notes.md"
Cohesion: 0.33
Nodes (5): Version 0.0.1, Version 0.0.2, Version 0.0.3, Version 0.1.0, Versionen 0.0.4 – 0.0.7

### Community 8 - "Mitglieder Management Portal"
Cohesion: 0.25
Nodes (7): Die Excel-Liste, Einstellungen, Für Entwickler, Installation, Mitglieder Management Portal, Regeln der Berechnung, So geht es

### Community 10 - "Members"
Cohesion: 0.09
Nodes (6): Config, Members, DataCheckTest, MemberListTest, SettingsTest, TemplateTest

### Community 12 - "test_store.py"
Cohesion: 0.09
Nodes (28): Aufbau, read_bytes(), add_member(), change(), append_log(), assign_numbers(), key_of(), log_text() (+20 more)

### Community 14 - "release"
Cohesion: 0.22
Nodes (9): jobs, release, name, permissions, contents, if, needs, permissions (+1 more)

### Community 15 - "steps"
Cohesion: 0.25
Nodes (9): steps, steps, continue-on-error, if, name, run, shell, timeout-minutes (+1 more)

### Community 16 - "version"
Cohesion: 0.22
Nodes (9): version, on, push, workflow_dispatch, branches, description, required, type (+1 more)

### Community 17 - "CLAUDE.md — member-admin ("Mitglieder Management Portal")"
Cohesion: 0.25
Nodes (7): CLAUDE.md — member-admin ("Mitglieder Management Portal"), Entwickeln (macOS/Windows), graphify, Neuer Chat — so einsteigen, Regeln für Änderungen, Verteilung / offene Punkte (Stand 2026-11-17), Was die App kann

### Community 18 - "build"
Cohesion: 0.33
Nodes (6): env, runs-on, timeout-minutes, QT_QPA_PLATFORM, build, env

### Community 19 - "strategy"
Cohesion: 0.33
Nodes (6): strategy, name, os, include, fail-fast, matrix

### Community 20 - "Member"
Cohesion: 0.09
Nodes (21): Member, 10. Geklärte Detailpunkte (2026-11-19), 1. Dateiformat (Schema-Version 1), 2. Sicheres Speichern, 3. Konfliktkopien, 4. Import-Assistent (QWizard), 5. Oberfläche, 6. Code (+13 more)

### Community 21 - "template.py"
Cohesion: 0.25
Nodes (16): add_check(), check_for(), date_check(), list_check(), number_check(), write_functions_sheet(), write_headings(), write_info_keys() (+8 more)

## Knowledge Gaps
- **6 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Members` connect `Members` to `club_file.py`, `birthday_calculation.py`, `main_window.py`, `MainWindow`, `test_store.py`, `Member`, `StandardFileTest`?**
  _High betweenness centrality (0.145) - this node is a cross-community bridge._
- **Are the 7 inferred relationships involving `Members` (e.g. with `Stand der Umsetzung` and `DataCheckTest`) actually correct?**
  _`Members` has 7 INFERRED edges - model-reasoned connections that need verification._
- **Should `club_file.py` be split into smaller, more focused modules?**
  _Cohesion score 0.0803633822501747 - nodes in this community are weakly interconnected._
- **Why does `Aufbau` connect `test_store.py` to `club_file.py`, `birthday_calculation.py`, `main_window.py`, `Members`, `CLAUDE.md — member-admin ("Mitglieder Management Portal")`, `Member`?**
  _High betweenness centrality (0.067) - this node is a cross-community bridge._
- **Are the 9 inferred relationships involving `MainWindow` (e.g. with `MemberListError` and `Members`) actually correct?**
  _`MainWindow` has 9 INFERRED edges - model-reasoned connections that need verification._
- **Should `birthday_calculation.py` be split into smaller, more focused modules?**
  _Cohesion score 0.07711711711711712 - nodes in this community are weakly interconnected._
- **Why does `MainWindow` connect `MainWindow` to `birthday_calculation.py`, `ResultPage`, `Members`, `main_window.py`?**
  _High betweenness centrality (0.063) - this node is a cross-community bridge._