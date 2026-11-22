# Graph Report - member-admin  (2026-11-22)

## Corpus Check
- 62 files · ~44,381 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 5 file(s) not represented in the graph (top: (none) 2, .ini 1, .iss 1)

## Summary
- 935 nodes · 2873 edges · 29 communities (23 shown, 6 thin omitted)
- Extraction: 92% EXTRACTED · 8% INFERRED · 0% AMBIGUOUS · INFERRED: 217 edges (avg confidence: 0.89)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `a6756445`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- with
- test_store.py
- birthday_calculation.py
- main_window.py
- mitgliederverwaltung.py
- MainWindow
- Member
- Release_Notes.md
- Mitglieder Management Portal
- .claude/CLAUDE.md
- template.py
- MemberDialog
- test_store.py
- release
- steps
- version
- ClubSettings
- build
- strategy
- CheckPage
- .write_rows
- MemberEditingUiTest
- ResultPage
- build.py
- MemberSheet
- club_file.py

## God Nodes (most connected - your core abstractions)
1. `save()` - 51 edges
2. `MainWindow` - 43 edges
3. `to_text()` - 40 edges
4. `Members` - 35 edges
5. `normalize()` - 33 edges
6. `Aufbau` - 32 edges
7. `muted()` - 31 edges
8. `update_member()` - 28 edges
9. `Stand der Umsetzung` - 25 edges
10. `Config` - 24 edges

## Surprising Connections (you probably didn't know these)
- `7. Tests` --references--> `is_standard()`  [INFERRED]
  PLAN_DATA_STORAGE.md → model/club_file.py
- `Stand der Umsetzung` --references--> `FileIndex`  [INFERRED]
  PLAN_DATA_STORAGE.md → logic/merge.py
- `Stand der Umsetzung` --references--> `MergeItem`  [INFERRED]
  PLAN_DATA_STORAGE.md → logic/merge.py
- `Aufbau` --references--> `Members`  [INFERRED]
  CLAUDE.md → model/members.py
- `Festlegungen (nicht rückgängig machen)` --references--> `SaveError`  [INFERRED]
  CLAUDE.md → store/errors.py

## Import Cycles
- None detected.

## Communities (29 total, 6 thin omitted)

### Community 0 - "with"
Cohesion: 0.18
Nodes (11): with, cache, cache-dependency-path, files, if-no-files-found, merge-multiple, name, path (+3 more)

### Community 1 - "test_store.py"
Cohesion: 0.07
Nodes (44): Aufbau, ConfigError, parse_numbers(), compare(), FileIndex, key(), member_values(), MergeItem (+36 more)

### Community 2 - "birthday_calculation.py"
Cohesion: 0.07
Nodes (30): find_birthdays(), is_birthday(), write_birthdays_into_ics(), write_birthdays_into_txt(), reminder(), with_gift(), write_entries_into_ics(), shift_years() (+22 more)

### Community 3 - "main_window.py"
Cohesion: 0.08
Nodes (18): shown(), IssuesPage, NumberItem, date_item(), MembersPage, SortItem, short_description(), make_card() (+10 more)

### Community 4 - "mitgliederverwaltung.py"
Cohesion: 0.10
Nodes (17): first_sheet_with_data(), guess_delimiter(), pick(), read_csv(), read_source(), read_xls(), read_xlsx(), Source (+9 more)

### Community 5 - "MainWindow"
Cohesion: 0.06
Nodes (12): file_hash(), write(), ImportUiTest, run(), run(), run(), run(), no_unexpected_import() (+4 more)

### Community 6 - "Member"
Cohesion: 0.06
Nodes (30): Ausgabe, Auswertungen, Bedienung und Betrieb, Daten und Excel (Fehler an der Quelle vermeiden), Ideen für das Mitglieder Management Portal, Kostenloser Download (2026-11-17 umgesetzt, live: tomegen.github.io/member-admin), Meine Reihenfolge, Mitglieder in der App pflegen (nur notiert, nicht umsetzen) (+22 more)

### Community 7 - "Release_Notes.md"
Cohesion: 0.25
Nodes (7): Version 0.0.1, Version 0.0.2, Version 0.0.3, Version 0.1.0, Version 0.2.0, Version 0.2.1, Versionen 0.0.4 – 0.0.7

### Community 8 - "Mitglieder Management Portal"
Cohesion: 0.20
Nodes (9): Die Mitgliederliste (Excel-Datei), Einstellungen, Für Entwickler, Gemeinsam nutzen und Sicherheit, Installation, Liste übernehmen (Import) und abgleichen, Mitglieder Management Portal, Regeln der Berechnung (+1 more)

### Community 10 - "template.py"
Cohesion: 0.23
Nodes (17): add_check(), check_for(), date_check(), list_check(), number_check(), write_functions_sheet(), write_headings(), write_info_keys() (+9 more)

### Community 11 - "MemberDialog"
Cohesion: 0.06
Nodes (13): given_fields(), ConflictDialog, DeleteDialog, MemberActions, change(), retry(), change(), choice_box() (+5 more)

### Community 12 - "test_store.py"
Cohesion: 0.09
Nodes (16): backup_folder(), update_member(), lock_owner(), owner_in(), save(), AddTest, DeleteTest, FunctionsTest (+8 more)

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
Nodes (12): CLAUDE.md — member-admin ("Mitglieder Management Portal"), Entwickeln (macOS/Windows), graphify, Neuer Chat — so einsteigen, Regeln für Änderungen, Verteilung / offene Punkte (Stand 2026-11-22), Was die App kann, ClubSettings (+4 more)

### Community 18 - "build"
Cohesion: 0.33
Nodes (6): env, runs-on, timeout-minutes, QT_QPA_PLATFORM, build, env

### Community 19 - "strategy"
Cohesion: 0.33
Nodes (6): strategy, name, os, include, fail-fast, matrix

### Community 20 - "CheckPage"
Cohesion: 0.10
Nodes (7): CheckPage, ColumnsPage, error_label(), make_table(), SourcePage, TargetPage, ValuesPage

### Community 21 - ".write_rows"
Cohesion: 0.07
Nodes (11): Config, MemberListError, Members, missing_columns_error(), Stand der Umsetzung, DataCheckTest, MemberListTest, SettingsTest (+3 more)

### Community 22 - "MemberEditingUiTest"
Cohesion: 0.08
Nodes (8): day(), DeleteUiTest, MemberEditingUiTest, fill_and_meanwhile_change_excel(), MergeUiTest, StandardFileBase, StandardFileUiTest, fill()

### Community 24 - "build.py"
Cohesion: 0.38
Nodes (4): find_inno_setup(), package(), package_mac(), package_windows()

### Community 27 - "club_file.py"
Cohesion: 0.06
Nodes (68): Festlegungen (nicht rückgängig machen), estimate_genders(), gender_of_first_name(), assign_numbers(), convert(), distinct_values(), guess_header_row(), ImportRow (+60 more)

## Knowledge Gaps
- **6 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Members` connect `.write_rows` to `test_store.py`, `birthday_calculation.py`, `main_window.py`, `mitgliederverwaltung.py`, `MainWindow`, `MemberDialog`, `test_store.py`, `club_file.py`?**
  _High betweenness centrality (0.066) - this node is a cross-community bridge._
- **Are the 7 inferred relationships involving `MainWindow` (e.g. with `MemberListError` and `Members`) actually correct?**
  _`MainWindow` has 7 INFERRED edges - model-reasoned connections that need verification._
- **Should `test_store.py` be split into smaller, more focused modules?**
  _Cohesion score 0.0694579681921454 - nodes in this community are weakly interconnected._
- **Why does `MainWindow` connect `MainWindow` to `birthday_calculation.py`, `main_window.py`, `MemberDialog`, `.write_rows`, `MemberEditingUiTest`, `ResultPage`, `club_file.py`?**
  _High betweenness centrality (0.048) - this node is a cross-community bridge._
- **Are the 9 inferred relationships involving `Members` (e.g. with `Aufbau` and `Stand der Umsetzung`) actually correct?**
  _`Members` has 9 INFERRED edges - model-reasoned connections that need verification._
- **Should `birthday_calculation.py` be split into smaller, more focused modules?**
  _Cohesion score 0.07071455016660497 - nodes in this community are weakly interconnected._
- **Why does `save()` connect `test_store.py` to `test_store.py`, `main_window.py`, `mitgliederverwaltung.py`, `MainWindow`, `template.py`, `MemberSheet`, `club_file.py`?**
  _High betweenness centrality (0.044) - this node is a cross-community bridge._