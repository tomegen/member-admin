# Graph Report - member-admin  (2026-11-14)

## Corpus Check
- 34 files · ~12,596 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 4 file(s) not represented in the graph (top: (none) 2, .ini 1, .ico 1)

## Summary
- 363 nodes · 885 edges · 15 communities (11 shown, 4 thin omitted)
- Extraction: 90% EXTRACTED · 10% INFERRED · 0% AMBIGUOUS · INFERRED: 87 edges (avg confidence: 0.9)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `f67346f1`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- with
- pandas
- birthday_calculation.py
- main_window.py
- build.py
- MainWindow
- Ideen für das Mitglieder Management Portal
- Release_Notes.md
- Mitglieder Management Portal
- .claude/CLAUDE.md
- Members
- ResultPage
- Config
- StatisticsPage

## God Nodes (most connected - your core abstractions)
1. `MainWindow` - 33 edges
2. `Members` - 31 edges
3. `Config` - 24 edges
4. `MemberListTest` - 22 edges
5. `make_member()` - 20 edges
6. `UiTest` - 20 edges
7. `ResultPage` - 19 edges
8. `find_birthdays()` - 14 edges
9. `Aufbau` - 14 edges
10. `shift_years()` - 14 edges

## Surprising Connections (you probably didn't know these)
- `Aufbau` --references--> `ConfigError`  [INFERRED]
  CLAUDE.md → config/config.py
- `Aufbau` --references--> `parse_numbers()`  [INFERRED]
  CLAUDE.md → config/config.py
- `Aufbau` --references--> `Config`  [INFERRED]
  CLAUDE.md → config/config.py
- `Aufbau` --references--> `age_on()`  [INFERRED]
  CLAUDE.md → model/checks.py
- `Aufbau` --references--> `Entry`  [INFERRED]
  CLAUDE.md → model/entry.py

## Import Cycles
- None detected.

## Communities (15 total, 4 thin omitted)

### Community 0 - "with"
Cohesion: 0.05
Nodes (47): env, runs-on, steps, strategy, timeout-minutes, QT_QPA_PLATFORM, name, os (+39 more)

### Community 1 - "pandas"
Cohesion: 0.09
Nodes (18): Aufbau, CLAUDE.md — member-admin ("Mitglieder Management Portal"), Entwickeln (macOS/Windows), Festlegungen (nicht rückgängig machen), graphify, Neuer Chat — so einsteigen, Regeln für Änderungen, Verteilung / offene Punkte (Stand 2026-11-14) (+10 more)

### Community 2 - "birthday_calculation.py"
Cohesion: 0.09
Nodes (25): find_birthdays(), is_birthday(), write_birthdays_into_ics(), write_birthdays_into_txt(), reminder(), write_entries_into_ics(), shift_years(), entries_to_rows() (+17 more)

### Community 3 - "main_window.py"
Cohesion: 0.13
Nodes (14): IssuesPage, NumberItem, default_year(), make_card(), OverviewPage, ResultSpec, save_file(), as_text() (+6 more)

### Community 5 - "MainWindow"
Cohesion: 0.11
Nodes (3): UiTest, MainWindow, WelcomePage

### Community 6 - "Ideen für das Mitglieder Management Portal"
Cohesion: 0.25
Nodes (7): Ausgabe, Auswertungen, Bedienung und Betrieb, Daten und Excel (Fehler an der Quelle vermeiden), Ideen für das Mitglieder Management Portal, Meine Reihenfolge, Verteilung und Technik (zurückgestellt oder offen)

### Community 7 - "Release_Notes.md"
Cohesion: 0.33
Nodes (5): Version 0.0.1, Version 0.0.2, Version 0.0.3, Version 0.1.0, Versionen 0.0.4 – 0.0.7

### Community 8 - "Mitglieder Management Portal"
Cohesion: 0.25
Nodes (7): Die Excel-Liste, Einstellungen, Für Entwickler, Installation, Mitglieder Management Portal, Regeln der Berechnung, So geht es

### Community 10 - "Members"
Cohesion: 0.16
Nodes (3): Members, DataCheckTest, MemberListTest

### Community 12 - "Config"
Cohesion: 0.10
Nodes (10): Config, ConfigError, parse_numbers(), write_statistics_into_xlsx(), write_member_template(), main(), smoke_test(), SettingsTest (+2 more)

### Community 14 - "StatisticsPage"
Cohesion: 0.19
Nodes (5): age_group_label(), Statistics, StatisticsTest, german_number(), StatisticsPage

## Knowledge Gaps
- **4 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Members` connect `Members` to `pandas`, `birthday_calculation.py`, `main_window.py`, `MainWindow`, `Config`?**
  _High betweenness centrality (0.094) - this node is a cross-community bridge._
- **Are the 10 inferred relationships involving `MainWindow` (e.g. with `UiTest` and `MemberListError`) actually correct?**
  _`MainWindow` has 10 INFERRED edges - model-reasoned connections that need verification._
- **Should `with` be split into smaller, more focused modules?**
  _Cohesion score 0.04521276595744681 - nodes in this community are weakly interconnected._
- **Why does `MainWindow` connect `MainWindow` to `pandas`, `birthday_calculation.py`, `main_window.py`, `Members`, `ResultPage`, `Config`, `StatisticsPage`?**
  _High betweenness centrality (0.094) - this node is a cross-community bridge._
- **Are the 5 inferred relationships involving `Members` (e.g. with `Issue` and `DataCheckTest`) actually correct?**
  _`Members` has 5 INFERRED edges - model-reasoned connections that need verification._
- **Should `pandas` be split into smaller, more focused modules?**
  _Cohesion score 0.08534850640113797 - nodes in this community are weakly interconnected._
- **Why does `Config` connect `Config` to `pandas`, `birthday_calculation.py`, `Members`, `MainWindow`?**
  _High betweenness centrality (0.052) - this node is a cross-community bridge._