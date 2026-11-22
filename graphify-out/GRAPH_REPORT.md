# Graph Report - member-admin  (2026-11-22)

## Corpus Check
- 59 files · ~39,011 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 5 file(s) not represented in the graph (top: (none) 2, .ini 1, .iss 1)

## Summary
- 859 nodes · 2549 edges · 26 communities (23 shown, 3 thin omitted)
- Extraction: 93% EXTRACTED · 7% INFERRED · 0% AMBIGUOUS · INFERRED: 181 edges (avg confidence: 0.89)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `2472449d`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- with
- club_file.py
- birthday_calculation.py
- main_window.py
- reader.py
- MainWindow
- Member
- Release_Notes.md
- Mitglieder Management Portal
- .claude/CLAUDE.md
- Members
- MemberDialog
- test_store.py
- CheckPage
- release
- steps
- version
- ClubSettings
- build
- strategy
- os
- template.py
- MemberEditingUiTest
- ResultPage
- Ideen für das Mitglieder Management Portal

## God Nodes (most connected - your core abstractions)
1. `Members` - 46 edges
2. `MainWindow` - 42 edges
3. `save()` - 42 edges
4. `to_text()` - 36 edges
5. `muted()` - 29 edges
6. `normalize()` - 28 edges
7. `Aufbau` - 26 edges
8. `Config` - 26 edges
9. `ClubSettings` - 25 edges
10. `MemberDialog` - 23 edges

## Surprising Connections (you probably didn't know these)
- `4. Import-Assistent (QWizard)` --references--> `detect_columns()`  [INFERRED]
  PLAN_DATA_STORAGE.md → model/columns.py
- `7. Tests` --references--> `is_standard()`  [INFERRED]
  PLAN_DATA_STORAGE.md → model/club_file.py
- `Mitglieder in der App pflegen (nur notiert, nicht umsetzen)` --references--> `detect_columns()`  [INFERRED]
  IDEAS.md → model/columns.py
- `Was die App kann` --references--> `ClubSettingsDialog`  [INFERRED]
  CLAUDE.md → ui/club_settings_dialog.py
- `Aufbau` --references--> `Config`  [INFERRED]
  CLAUDE.md → config/config.py

## Import Cycles
- None detected.

## Communities (26 total, 3 thin omitted)

### Community 0 - "with"
Cohesion: 0.18
Nodes (11): with, cache, cache-dependency-path, files, if-no-files-found, merge-multiple, name, path (+3 more)

### Community 1 - "club_file.py"
Cohesion: 0.06
Nodes (64): estimate_genders(), gender_of_first_name(), assign_numbers(), convert(), distinct_values(), guess_header_row(), ImportRow, is_missing() (+56 more)

### Community 2 - "birthday_calculation.py"
Cohesion: 0.07
Nodes (34): find_birthdays(), is_birthday(), write_birthdays_into_ics(), write_birthdays_into_txt(), reminder(), with_gift(), write_entries_into_ics(), shift_years() (+26 more)

### Community 3 - "main_window.py"
Cohesion: 0.07
Nodes (22): main(), take_screenshots(), shown(), IssuesPage, NumberItem, date_item(), MembersPage, SortItem (+14 more)

### Community 4 - "reader.py"
Cohesion: 0.10
Nodes (18): first_sheet_with_data(), guess_delimiter(), pick(), read_csv(), read_source(), read_xls(), read_xlsx(), Source (+10 more)

### Community 5 - "MainWindow"
Cohesion: 0.07
Nodes (9): file_hash(), day(), ImportUiTest, run(), run(), run(), UiTest, MainWindow (+1 more)

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
Cohesion: 0.10
Nodes (6): Festlegungen (nicht rückgängig machen), MemberListError, Members, DataCheckTest, MemberListTest, StandardFileTest

### Community 11 - "MemberDialog"
Cohesion: 0.10
Nodes (10): ConflictDialog, MemberActions, change(), retry(), change(), choice_box(), DateField, ExitDialog (+2 more)

### Community 12 - "test_store.py"
Cohesion: 0.05
Nodes (41): Aufbau, ConfigError, parse_numbers(), function_key(), backup_folder(), backups_of(), rotate(), write_backup() (+33 more)

### Community 13 - "CheckPage"
Cohesion: 0.09
Nodes (8): CheckPage, ColumnsPage, error_label(), ImportWizard, make_table(), SourcePage, TargetPage, ValuesPage

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

### Community 20 - "os"
Cohesion: 0.38
Nodes (4): find_inno_setup(), package(), package_mac(), package_windows()

### Community 21 - "template.py"
Cohesion: 0.10
Nodes (20): Config, add_check(), check_for(), date_check(), list_check(), number_check(), write_functions_sheet(), write_headings() (+12 more)

### Community 22 - "MemberEditingUiTest"
Cohesion: 0.16
Nodes (5): MemberEditingUiTest, fill_and_meanwhile_change_excel(), StandardFileBase, StandardFileUiTest, fill()

### Community 24 - "Ideen für das Mitglieder Management Portal"
Cohesion: 0.18
Nodes (10): Ausgabe, Auswertungen, Bedienung und Betrieb, Daten und Excel (Fehler an der Quelle vermeiden), Ideen für das Mitglieder Management Portal, Kostenloser Download (2026-11-17 umgesetzt, live: tomegen.github.io/member-admin), Meine Reihenfolge, Mitglieder in der App pflegen (nur notiert, nicht umsetzen) (+2 more)

## Knowledge Gaps
- **3 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Members` connect `Members` to `club_file.py`, `birthday_calculation.py`, `main_window.py`, `reader.py`, `MainWindow`, `Member`, `test_store.py`, `ClubSettings`, `template.py`?**
  _High betweenness centrality (0.092) - this node is a cross-community bridge._
- **Are the 7 inferred relationships involving `Members` (e.g. with `ClubSettings` and `Stand der Umsetzung`) actually correct?**
  _`Members` has 7 INFERRED edges - model-reasoned connections that need verification._
- **Should `club_file.py` be split into smaller, more focused modules?**
  _Cohesion score 0.05761862658414382 - nodes in this community are weakly interconnected._
- **Why does `Aufbau` connect `test_store.py` to `club_file.py`, `birthday_calculation.py`, `main_window.py`, `reader.py`, `MainWindow`, `Member`, `Members`, `MemberDialog`, `ClubSettings`, `template.py`?**
  _High betweenness centrality (0.045) - this node is a cross-community bridge._
- **Are the 6 inferred relationships involving `MainWindow` (e.g. with `ImportUiTest` and `StandardFileBase`) actually correct?**
  _`MainWindow` has 6 INFERRED edges - model-reasoned connections that need verification._
- **Should `birthday_calculation.py` be split into smaller, more focused modules?**
  _Cohesion score 0.07098765432098765 - nodes in this community are weakly interconnected._
- **Why does `MainWindow` connect `MainWindow` to `birthday_calculation.py`, `main_window.py`, `reader.py`, `test_store.py`, `CheckPage`, `template.py`, `MemberEditingUiTest`, `ResultPage`?**
  _High betweenness centrality (0.044) - this node is a cross-community bridge._