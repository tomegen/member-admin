# Graph Report - member-admin  (2026-11-14)

## Corpus Check
- 24 files · ~8,227 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 4 file(s) not represented in the graph (top: (none) 2, .ini 1, .ico 1)

## Summary
- 259 nodes · 566 edges · 15 communities (11 shown, 4 thin omitted)
- Extraction: 90% EXTRACTED · 10% INFERRED · 0% AMBIGUOUS · INFERRED: 54 edges (avg confidence: 0.9)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `a4fed48e`
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
- version
- IssuesPage

## God Nodes (most connected - your core abstractions)
1. `Members` - 25 edges
2. `MainWindow` - 25 edges
3. `MemberListTest` - 22 edges
4. `ResultPage` - 17 edges
5. `UiTest` - 15 edges
6. `Config` - 14 edges
7. `shift_years()` - 12 edges
8. `make_member()` - 12 edges
9. `with` - 12 edges
10. `Aufbau` - 11 edges

## Surprising Connections (you probably didn't know these)
- `Aufbau` --references--> `Config`  [INFERRED]
  CLAUDE.md → config/config.py
- `Aufbau` --references--> `ConfigError`  [INFERRED]
  CLAUDE.md → config/config.py
- `Aufbau` --references--> `shift_years()`  [INFERRED]
  CLAUDE.md → logic/date_utils.py
- `Aufbau` --references--> `Entry`  [INFERRED]
  CLAUDE.md → model/entry.py
- `Aufbau` --references--> `ResultSpec`  [INFERRED]
  CLAUDE.md → ui/result_page.py

## Import Cycles
- None detected.

## Communities (15 total, 4 thin omitted)

### Community 0 - "with"
Cohesion: 0.06
Nodes (38): env, runs-on, steps, strategy, timeout-minutes, QT_QPA_PLATFORM, name, os (+30 more)

### Community 1 - "pandas"
Cohesion: 0.11
Nodes (17): Aufbau, CLAUDE.md — member-admin ("Mitglieder Management Portal"), Entwickeln (macOS/Windows), Festlegungen (nicht rückgängig machen), graphify, Neuer Chat — so einsteigen, Regeln für Änderungen, Verteilung / offene Punkte (Stand 2026-11-14) (+9 more)

### Community 2 - "birthday_calculation.py"
Cohesion: 0.14
Nodes (12): find_birthdays(), is_birthday(), write_birthdays_into_ics(), write_birthdays_into_txt(), shift_years(), find_honors(), is_honor(), write_honors_into_txt() (+4 more)

### Community 3 - "main_window.py"
Cohesion: 0.17
Nodes (11): ConfigError, main(), smoke_test(), make_card(), OverviewPage, ResultSpec, apply_theme(), heading() (+3 more)

### Community 5 - "MainWindow"
Cohesion: 0.15
Nodes (3): UiTest, MainWindow, WelcomePage

### Community 6 - "Ideen für das Mitglieder Management Portal"
Cohesion: 0.25
Nodes (7): Ausgabe, Auswertungen, Bedienung und Betrieb, Daten und Excel (Fehler an der Quelle vermeiden), Ideen für das Mitglieder Management Portal, Meine Reihenfolge, Verteilung und Technik (zurückgestellt oder offen)

### Community 7 - "Release_Notes.md"
Cohesion: 0.33
Nodes (5): Version 0.0.1, Version 0.0.2, Version 0.0.3, Version 0.1.0, Versionen 0.0.4 – 0.0.7

### Community 8 - "Mitglieder Management Portal"
Cohesion: 0.25
Nodes (7): Die Excel-Liste, Einstellungen (`config.ini`), Für Entwickler, Installation, Mitglieder Management Portal, Regeln der Berechnung, So geht es

### Community 10 - "Members"
Cohesion: 0.18
Nodes (3): Config, Members, MemberListTest

### Community 11 - "ResultPage"
Cohesion: 0.19
Nodes (3): default_year(), DateItem, ResultPage

### Community 12 - "version"
Cohesion: 0.22
Nodes (9): version, on, push, workflow_dispatch, branches, description, required, type (+1 more)

## Knowledge Gaps
- **4 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Members` connect `Members` to `pandas`, `birthday_calculation.py`, `main_window.py`, `MainWindow`?**
  _High betweenness centrality (0.092) - this node is a cross-community bridge._
- **Are the 3 inferred relationships involving `Members` (e.g. with `Member` and `MemberListTest`) actually correct?**
  _`Members` has 3 INFERRED edges - model-reasoned connections that need verification._
- **Should `with` be split into smaller, more focused modules?**
  _Cohesion score 0.05668016194331984 - nodes in this community are weakly interconnected._
- **Why does `MainWindow` connect `MainWindow` to `pandas`, `main_window.py`, `Members`, `ResultPage`, `IssuesPage`?**
  _High betweenness centrality (0.090) - this node is a cross-community bridge._
- **Are the 8 inferred relationships involving `MainWindow` (e.g. with `UiTest` and `MemberListError`) actually correct?**
  _`MainWindow` has 8 INFERRED edges - model-reasoned connections that need verification._
- **Should `pandas` be split into smaller, more focused modules?**
  _Cohesion score 0.10804597701149425 - nodes in this community are weakly interconnected._
- **Why does `ResultPage` connect `ResultPage` to `main_window.py`, `MainWindow`?**
  _High betweenness centrality (0.053) - this node is a cross-community bridge._