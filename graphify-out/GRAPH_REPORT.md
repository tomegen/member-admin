# Graph Report - member-admin  (2026-11-22)

## Corpus Check
- 47 files · ~28,398 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 5 file(s) not represented in the graph (top: (none) 2, .ini 1, .iss 1)

## Summary
- 619 nodes · 1730 edges · 23 communities (18 shown, 5 thin omitted)
- Extraction: 93% EXTRACTED · 7% INFERRED · 0% AMBIGUOUS · INFERRED: 126 edges (avg confidence: 0.9)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `e85fe8d1`
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
- ClubSettings
- build
- strategy
- template.py
- StandardFileTest

## God Nodes (most connected - your core abstractions)
1. `Members` - 41 edges
2. `save()` - 39 edges
3. `MainWindow` - 32 edges
4. `Aufbau` - 26 edges
5. `ClubSettings` - 24 edges
6. `Config` - 23 edges
7. `make_member()` - 23 edges
8. `MemberListTest` - 20 edges
9. `ResultPage` - 20 edges
10. `UiTest` - 20 edges

## Surprising Connections (you probably didn't know these)
- `7. Tests` --references--> `is_standard()`  [INFERRED]
  PLAN_DATA_STORAGE.md → model/club_file.py
- `Aufbau` --references--> `update_member()`  [INFERRED]
  CLAUDE.md → store/changes.py
- `Aufbau` --references--> `add_member()`  [INFERRED]
  CLAUDE.md → store/changes.py
- `Stand der Umsetzung` --references--> `update_settings()`  [INFERRED]
  PLAN_DATA_STORAGE.md → store/changes.py
- `Aufbau` --references--> `Conflict`  [INFERRED]
  CLAUDE.md → store/errors.py

## Import Cycles
- None detected.

## Communities (23 total, 5 thin omitted)

### Community 0 - "with"
Cohesion: 0.18
Nodes (11): with, cache, cache-dependency-path, files, if-no-files-found, merge-multiple, name, path (+3 more)

### Community 1 - "club_file.py"
Cohesion: 0.06
Nodes (54): Aufbau, Festlegungen (nicht rückgängig machen), age_group_label(), age_on(), plausibility_issues(), cell_key(), choice(), file_hash() (+46 more)

### Community 2 - "birthday_calculation.py"
Cohesion: 0.07
Nodes (30): find_birthdays(), is_birthday(), write_birthdays_into_ics(), write_birthdays_into_txt(), reminder(), with_gift(), write_entries_into_ics(), shift_years() (+22 more)

### Community 3 - "main_window.py"
Cohesion: 0.07
Nodes (23): ConfigError, parse_numbers(), write_statistics_into_xlsx(), main(), smoke_test(), take_screenshots(), IssuesPage, NumberItem (+15 more)

### Community 4 - "os"
Cohesion: 0.09
Nodes (18): find_inno_setup(), package(), package_mac(), package_windows(), backup_folder(), backups_of(), rotate(), write_backup() (+10 more)

### Community 5 - "MainWindow"
Cohesion: 0.10
Nodes (3): StandardFileUiTest, UiTest, MainWindow

### Community 6 - "detect_columns"
Cohesion: 0.06
Nodes (29): Ausgabe, Auswertungen, Bedienung und Betrieb, Daten und Excel (Fehler an der Quelle vermeiden), Ideen für das Mitglieder Management Portal, Kostenloser Download (2026-11-17 umgesetzt, live: tomegen.github.io/member-admin), Meine Reihenfolge, Mitglieder in der App pflegen (nur notiert, nicht umsetzen) (+21 more)

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
Cohesion: 0.12
Nodes (14): read_bytes(), add_member(), change(), update_member(), update_settings(), save(), AddTest, NumbersTest (+6 more)

### Community 14 - "release"
Cohesion: 0.22
Nodes (9): jobs, release, name, permissions, contents, if, needs, permissions (+1 more)

### Community 15 - "steps"
Cohesion: 0.25
Nodes (9): steps, steps, continue-on-error, if, name, run, shell, timeout-minutes (+1 more)

### Community 16 - "version"
Cohesion: 0.22
Nodes (9): version, on, push, workflow_dispatch, branches, description, required, type (+1 more)

### Community 17 - "ClubSettings"
Cohesion: 0.09
Nodes (12): CLAUDE.md — member-admin ("Mitglieder Management Portal"), Entwickeln (macOS/Windows), graphify, Neuer Chat — so einsteigen, Regeln für Änderungen, Verteilung / offene Punkte (Stand 2026-11-17), Was die App kann, ClubSettings (+4 more)

### Community 18 - "build"
Cohesion: 0.33
Nodes (6): env, runs-on, timeout-minutes, QT_QPA_PLATFORM, build, env

### Community 19 - "strategy"
Cohesion: 0.33
Nodes (6): strategy, name, os, include, fail-fast, matrix

### Community 21 - "template.py"
Cohesion: 0.26
Nodes (16): add_check(), check_for(), date_check(), list_check(), number_check(), write_functions_sheet(), write_headings(), write_info_keys() (+8 more)

## Knowledge Gaps
- **5 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Members` connect `Members` to `club_file.py`, `birthday_calculation.py`, `main_window.py`, `os`, `MainWindow`, `test_store.py`, `ClubSettings`, `StandardFileTest`?**
  _High betweenness centrality (0.111) - this node is a cross-community bridge._
- **Are the 6 inferred relationships involving `Members` (e.g. with `ClubSettings` and `Stand der Umsetzung`) actually correct?**
  _`Members` has 6 INFERRED edges - model-reasoned connections that need verification._
- **Should `club_file.py` be split into smaller, more focused modules?**
  _Cohesion score 0.06405856783344772 - nodes in this community are weakly interconnected._
- **Why does `save()` connect `test_store.py` to `club_file.py`, `birthday_calculation.py`, `main_window.py`, `os`, `MainWindow`, `template.py`?**
  _High betweenness centrality (0.058) - this node is a cross-community bridge._
- **Are the 2 inferred relationships involving `MainWindow` (e.g. with `StandardFileUiTest` and `UiTest`) actually correct?**
  _`MainWindow` has 2 INFERRED edges - model-reasoned connections that need verification._
- **Should `birthday_calculation.py` be split into smaller, more focused modules?**
  _Cohesion score 0.07433489827856025 - nodes in this community are weakly interconnected._
- **Why does `Aufbau` connect `club_file.py` to `birthday_calculation.py`, `main_window.py`, `os`, `MainWindow`, `detect_columns`, `Members`, `test_store.py`, `ClubSettings`?**
  _High betweenness centrality (0.057) - this node is a cross-community bridge._