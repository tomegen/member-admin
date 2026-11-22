# Graph Report - member-admin  (2026-11-22)

## Corpus Check
- 62 files · ~42,068 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 5 file(s) not represented in the graph (top: (none) 2, .ini 1, .iss 1)

## Summary
- 914 nodes · 2777 edges · 34 communities (27 shown, 7 thin omitted)
- Extraction: 93% EXTRACTED · 7% INFERRED · 0% AMBIGUOUS · INFERRED: 207 edges (avg confidence: 0.89)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `46725678`
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
- test_ui.py
- import_wizard.py
- suggest_columns
- CheckPage
- read_source
- Table

## God Nodes (most connected - your core abstractions)
1. `Members` - 51 edges
2. `MainWindow` - 46 edges
3. `save()` - 43 edges
4. `to_text()` - 39 edges
5. `muted()` - 31 edges
6. `normalize()` - 30 edges
7. `Aufbau` - 27 edges
8. `Config` - 26 edges
9. `update_member()` - 24 edges
10. `ClubSettings` - 23 edges

## Surprising Connections (you probably didn't know these)
- `4. Import-Assistent (QWizard)` --references--> `detect_columns()`  [INFERRED]
  PLAN_DATA_STORAGE.md → model/columns.py
- `7. Tests` --references--> `is_standard()`  [INFERRED]
  PLAN_DATA_STORAGE.md → model/club_file.py
- `Aufbau` --references--> `MemberListError`  [INFERRED]
  CLAUDE.md → model/members.py
- `Stand der Umsetzung` --references--> `Members`  [INFERRED]
  PLAN_DATA_STORAGE.md → model/members.py
- `Stand der Umsetzung` --references--> `merge_members()`  [INFERRED]
  PLAN_DATA_STORAGE.md → store/changes.py

## Import Cycles
- None detected.

## Communities (34 total, 7 thin omitted)

### Community 0 - "with"
Cohesion: 0.18
Nodes (11): with, cache, cache-dependency-path, files, if-no-files-found, merge-multiple, name, path (+3 more)

### Community 1 - "club_file.py"
Cohesion: 0.09
Nodes (47): Festlegungen (nicht rückgängig machen), write_standard_file(), cell_key(), choice(), heading_columns(), headings(), is_standard(), members_sheet() (+39 more)

### Community 2 - "birthday_calculation.py"
Cohesion: 0.07
Nodes (33): find_birthdays(), is_birthday(), write_birthdays_into_ics(), write_birthdays_into_txt(), reminder(), with_gift(), write_entries_into_ics(), shift_years() (+25 more)

### Community 3 - "main_window.py"
Cohesion: 0.07
Nodes (23): parse_numbers(), shown(), IssuesPage, NumberItem, default_year(), date_item(), MembersPage, SortItem (+15 more)

### Community 4 - "reader.py"
Cohesion: 0.21
Nodes (12): first_sheet_with_data(), guess_delimiter(), is_empty_row(), pick(), read_csv(), read_xls(), read_xlsx(), Source (+4 more)

### Community 5 - "MainWindow"
Cohesion: 0.06
Nodes (10): file_hash(), day(), ImportUiTest, run(), run(), run(), no_unexpected_import(), UiTest (+2 more)

### Community 6 - "Member"
Cohesion: 0.07
Nodes (29): compare(), FileIndex, key(), member_values(), MergeItem, name_key(), Member, 10. Geklärte Detailpunkte (2026-11-19) (+21 more)

### Community 7 - "Release_Notes.md"
Cohesion: 0.33
Nodes (5): Version 0.0.1, Version 0.0.2, Version 0.0.3, Version 0.1.0, Versionen 0.0.4 – 0.0.7

### Community 8 - "Mitglieder Management Portal"
Cohesion: 0.25
Nodes (7): Die Excel-Liste, Einstellungen, Für Entwickler, Installation, Mitglieder Management Portal, Regeln der Berechnung, So geht es

### Community 10 - "Members"
Cohesion: 0.11
Nodes (4): Members, DataCheckTest, MemberListTest, StandardFileTest

### Community 11 - "MemberDialog"
Cohesion: 0.07
Nodes (12): given_fields(), ConflictDialog, MemberActions, change(), retry(), change(), choice_box(), DateField (+4 more)

### Community 12 - "test_store.py"
Cohesion: 0.06
Nodes (42): Aufbau, function_key(), backup_folder(), backups_of(), rotate(), write_backup(), add_member(), change() (+34 more)

### Community 13 - "CheckPage"
Cohesion: 0.14
Nodes (5): ColumnsPage, error_label(), make_table(), TargetPage, ValuesPage

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
Cohesion: 0.21
Nodes (16): add_check(), check_for(), date_check(), list_check(), number_check(), write_functions_sheet(), write_headings(), write_info_keys() (+8 more)

### Community 22 - "MemberEditingUiTest"
Cohesion: 0.11
Nodes (6): MemberEditingUiTest, fill_and_meanwhile_change_excel(), MergeUiTest, StandardFileBase, StandardFileUiTest, fill()

### Community 24 - "Ideen für das Mitglieder Management Portal"
Cohesion: 0.12
Nodes (12): Ausgabe, Auswertungen, Bedienung und Betrieb, Daten und Excel (Fehler an der Quelle vermeiden), Ideen für das Mitglieder Management Portal, Kostenloser Download (2026-11-17 umgesetzt, live: tomegen.github.io/member-admin), Meine Reihenfolge, Mitglieder in der App pflegen (nur notiert, nicht umsetzen) (+4 more)

### Community 26 - "test_ui.py"
Cohesion: 0.12
Nodes (9): Config, ConfigError, guess_header_row(), known_headings(), main(), smoke_test(), take_screenshots(), SettingsTest (+1 more)

### Community 27 - "import_wizard.py"
Cohesion: 0.17
Nodes (11): estimate_genders(), gender_of_first_name(), assign_numbers(), convert(), distinct_values(), ImportRow, is_missing(), split_name() (+3 more)

### Community 28 - "suggest_columns"
Cohesion: 0.24
Nodes (6): share(), suggest_columns(), ConvertTest, ImportTest, MappingTest, WriterTest

### Community 30 - "read_source"
Cohesion: 0.38
Nodes (3): read_source(), SourceError, ReaderTest

## Knowledge Gaps
- **7 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Members` connect `Members` to `club_file.py`, `birthday_calculation.py`, `main_window.py`, `MainWindow`, `Member`, `MemberDialog`, `test_store.py`, `template.py`, `test_ui.py`, `import_wizard.py`, `suggest_columns`?**
  _High betweenness centrality (0.094) - this node is a cross-community bridge._
- **Are the 9 inferred relationships involving `Members` (e.g. with `Stand der Umsetzung` and `DataCheckTest`) actually correct?**
  _`Members` has 9 INFERRED edges - model-reasoned connections that need verification._
- **Should `club_file.py` be split into smaller, more focused modules?**
  _Cohesion score 0.08860759493670886 - nodes in this community are weakly interconnected._
- **Why does `MainWindow` connect `MainWindow` to `club_file.py`, `birthday_calculation.py`, `main_window.py`, `Members`, `MemberDialog`, `MemberEditingUiTest`, `ResultPage`, `test_ui.py`?**
  _High betweenness centrality (0.052) - this node is a cross-community bridge._
- **Are the 8 inferred relationships involving `MainWindow` (e.g. with `ImportUiTest` and `StandardFileBase`) actually correct?**
  _`MainWindow` has 8 INFERRED edges - model-reasoned connections that need verification._
- **Should `birthday_calculation.py` be split into smaller, more focused modules?**
  _Cohesion score 0.07367737747484583 - nodes in this community are weakly interconnected._
- **Why does `Aufbau` connect `test_store.py` to `club_file.py`, `birthday_calculation.py`, `main_window.py`, `reader.py`, `MainWindow`, `Member`, `MemberDialog`, `ClubSettings`, `Ideen für das Mitglieder Management Portal`, `test_ui.py`?**
  _High betweenness centrality (0.040) - this node is a cross-community bridge._