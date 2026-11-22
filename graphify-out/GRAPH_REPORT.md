# Graph Report - member-admin  (2026-11-22)

## Corpus Check
- 52 files · ~32,806 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 5 file(s) not represented in the graph (top: (none) 2, .ini 1, .iss 1)

## Summary
- 732 nodes · 2097 edges · 25 communities (22 shown, 3 thin omitted)
- Extraction: 92% EXTRACTED · 8% INFERRED · 0% AMBIGUOUS · INFERRED: 165 edges (avg confidence: 0.89)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `e03f608f`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- with
- club_file.py
- birthday_calculation.py
- main_window.py
- changes.py
- MainWindow
- Member
- Release_Notes.md
- Mitglieder Management Portal
- .claude/CLAUDE.md
- Members
- MemberDialog
- test_store.py
- release
- steps
- version
- ClubSettings
- build
- strategy
- os
- template.py
- MemberEditingUiTest
- Ideen für das Mitglieder Management Portal

## God Nodes (most connected - your core abstractions)
1. `Members` - 44 edges
2. `save()` - 42 edges
3. `MainWindow` - 40 edges
4. `ClubSettings` - 26 edges
5. `Aufbau` - 26 edges
6. `muted()` - 25 edges
7. `MemberDialog` - 24 edges
8. `update_member()` - 23 edges
9. `make_member()` - 23 edges
10. `Config` - 23 edges

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

## Communities (25 total, 3 thin omitted)

### Community 0 - "with"
Cohesion: 0.18
Nodes (11): with, cache, cache-dependency-path, files, if-no-files-found, merge-multiple, name, path (+3 more)

### Community 1 - "club_file.py"
Cohesion: 0.08
Nodes (36): Festlegungen (nicht rückgängig machen), cell_key(), choice(), heading_columns(), headings(), is_standard(), is_standard_file(), members_sheet() (+28 more)

### Community 2 - "birthday_calculation.py"
Cohesion: 0.06
Nodes (37): find_birthdays(), is_birthday(), write_birthdays_into_ics(), write_birthdays_into_txt(), reminder(), with_gift(), write_entries_into_ics(), shift_years() (+29 more)

### Community 3 - "main_window.py"
Cohesion: 0.05
Nodes (21): parse_numbers(), shown(), IssuesPage, NumberItem, date_item(), MembersPage, SortItem, make_card() (+13 more)

### Community 4 - "changes.py"
Cohesion: 0.10
Nodes (35): Aufbau, general_text(), function_key(), add_member(), change(), append_log(), area_text(), assign_numbers() (+27 more)

### Community 5 - "MainWindow"
Cohesion: 0.10
Nodes (4): file_hash(), StandardFileBase, UiTest, MainWindow

### Community 6 - "Member"
Cohesion: 0.09
Nodes (21): Member, 10. Geklärte Detailpunkte (2026-11-19), 1. Dateiformat (Schema-Version 1), 2. Sicheres Speichern, 3. Konfliktkopien, 4. Import-Assistent (QWizard), 5. Oberfläche, 6. Code (+13 more)

### Community 7 - "Release_Notes.md"
Cohesion: 0.33
Nodes (5): Version 0.0.1, Version 0.0.2, Version 0.0.3, Version 0.1.0, Versionen 0.0.4 – 0.0.7

### Community 8 - "Mitglieder Management Portal"
Cohesion: 0.25
Nodes (7): Die Excel-Liste, Einstellungen, Für Entwickler, Installation, Mitglieder Management Portal, Regeln der Berechnung, So geht es

### Community 10 - "Members"
Cohesion: 0.07
Nodes (7): Config, Members, DataCheckTest, MemberListTest, SettingsTest, StandardFileTest, TemplateTest

### Community 11 - "MemberDialog"
Cohesion: 0.10
Nodes (10): ConflictDialog, MemberActions, change(), retry(), change(), choice_box(), DateField, ExitDialog (+2 more)

### Community 12 - "test_store.py"
Cohesion: 0.11
Nodes (14): read_bytes(), backup_folder(), update_member(), save(), AddTest, FunctionsTest, write(), NumbersTest (+6 more)

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
Cohesion: 0.07
Nodes (13): CLAUDE.md — member-admin ("Mitglieder Management Portal"), Entwickeln (macOS/Windows), graphify, Neuer Chat — so einsteigen, Regeln für Änderungen, Verteilung / offene Punkte (Stand 2026-11-17), Was die App kann, ClubSettings (+5 more)

### Community 18 - "build"
Cohesion: 0.33
Nodes (6): env, runs-on, timeout-minutes, QT_QPA_PLATFORM, build, env

### Community 19 - "strategy"
Cohesion: 0.33
Nodes (6): strategy, name, os, include, fail-fast, matrix

### Community 20 - "os"
Cohesion: 0.20
Nodes (8): find_inno_setup(), package(), package_mac(), package_windows(), backups_of(), rotate(), write_backup(), BackupTest

### Community 21 - "template.py"
Cohesion: 0.13
Nodes (21): ConfigError, add_check(), check_for(), date_check(), list_check(), number_check(), write_functions_sheet(), write_headings() (+13 more)

### Community 22 - "MemberEditingUiTest"
Cohesion: 0.22
Nodes (3): MemberEditingUiTest, fill_and_meanwhile_change_excel(), fill()

### Community 24 - "Ideen für das Mitglieder Management Portal"
Cohesion: 0.18
Nodes (10): Ausgabe, Auswertungen, Bedienung und Betrieb, Daten und Excel (Fehler an der Quelle vermeiden), Ideen für das Mitglieder Management Portal, Kostenloser Download (2026-11-17 umgesetzt, live: tomegen.github.io/member-admin), Meine Reihenfolge, Mitglieder in der App pflegen (nur notiert, nicht umsetzen) (+2 more)

## Knowledge Gaps
- **3 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Members` connect `Members` to `club_file.py`, `birthday_calculation.py`, `main_window.py`, `changes.py`, `MainWindow`, `Member`, `test_store.py`, `ClubSettings`, `template.py`?**
  _High betweenness centrality (0.103) - this node is a cross-community bridge._
- **Are the 8 inferred relationships involving `Members` (e.g. with `ClubSettings` and `Stand der Umsetzung`) actually correct?**
  _`Members` has 8 INFERRED edges - model-reasoned connections that need verification._
- **Should `club_file.py` be split into smaller, more focused modules?**
  _Cohesion score 0.08105022831050228 - nodes in this community are weakly interconnected._
- **Why does `MainWindow` connect `MainWindow` to `club_file.py`, `birthday_calculation.py`, `main_window.py`, `Members`, `MemberDialog`, `template.py`?**
  _High betweenness centrality (0.057) - this node is a cross-community bridge._
- **Are the 7 inferred relationships involving `MainWindow` (e.g. with `StandardFileBase` and `UiTest`) actually correct?**
  _`MainWindow` has 7 INFERRED edges - model-reasoned connections that need verification._
- **Should `birthday_calculation.py` be split into smaller, more focused modules?**
  _Cohesion score 0.06335204490777867 - nodes in this community are weakly interconnected._
- **Why does `Aufbau` connect `changes.py` to `club_file.py`, `birthday_calculation.py`, `main_window.py`, `MainWindow`, `Member`, `Members`, `MemberDialog`, `test_store.py`, `ClubSettings`, `template.py`?**
  _High betweenness centrality (0.053) - this node is a cross-community bridge._