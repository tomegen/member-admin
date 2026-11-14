# Graph Report - member-admin  (2026-11-14)

## Corpus Check
- 23 files · ~7,353 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 4 file(s) not represented in the graph (top: (none) 2, .ini 1, .ico 1)

## Summary
- 251 nodes · 559 edges · 14 communities (9 shown, 5 thin omitted)
- Extraction: 90% EXTRACTED · 10% INFERRED · 0% AMBIGUOUS · INFERRED: 54 edges (avg confidence: 0.9)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `8b552499`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- with
- pandas
- birthday_calculation.py
- main_window.py
- test_regressions.py
- MainWindow
- CLAUDE.md — member-admin ("Mitglieder Management Portal")
- Release_Notes.md
- Mitglieder Management Portal
- .claude/CLAUDE.md
- Members
- ResultPage
- version

## God Nodes (most connected - your core abstractions)
1. `Members` - 25 edges
2. `MainWindow` - 25 edges
3. `MemberListTest` - 22 edges
4. `ResultPage` - 17 edges
5. `UiTest` - 15 edges
6. `Config` - 14 edges
7. `with` - 12 edges
8. `make_member()` - 12 edges
9. `shift_years()` - 12 edges
10. `find_birthdays()` - 11 edges

## Surprising Connections (you probably didn't know these)
- `Aufbau` --references--> `Entry`  [INFERRED]
  CLAUDE.md → model/entry.py
- `Aufbau` --references--> `Member`  [INFERRED]
  CLAUDE.md → model/member.py
- `Aufbau` --references--> `MemberListError`  [INFERRED]
  CLAUDE.md → model/members.py
- `Aufbau` --references--> `Issue`  [INFERRED]
  CLAUDE.md → model/members.py
- `Aufbau` --references--> `parse_date()`  [INFERRED]
  CLAUDE.md → model/members.py

## Import Cycles
- None detected.

## Communities (14 total, 5 thin omitted)

### Community 0 - "with"
Cohesion: 0.06
Nodes (38): env, runs-on, steps, strategy, timeout-minutes, QT_QPA_PLATFORM, name, os (+30 more)

### Community 1 - "pandas"
Cohesion: 0.16
Nodes (9): Festlegungen (nicht rückgängig machen), entries_to_rows(), write_entries_into_xlsx(), format_date(), Member, Issue, MemberListError, parse_date() (+1 more)

### Community 2 - "birthday_calculation.py"
Cohesion: 0.14
Nodes (13): find_birthdays(), is_birthday(), write_birthdays_into_ics(), write_birthdays_into_txt(), shift_years(), find_honors(), is_honor(), write_honors_into_txt() (+5 more)

### Community 3 - "main_window.py"
Cohesion: 0.15
Nodes (10): IssuesPage, NumberItem, make_card(), OverviewPage, ResultSpec, heading(), muted(), primary_button() (+2 more)

### Community 4 - "test_regressions.py"
Cohesion: 0.12
Nodes (7): package(), Aufbau, Config, ConfigError, main(), smoke_test(), apply_theme()

### Community 6 - "CLAUDE.md — member-admin ("Mitglieder Management Portal")"
Cohesion: 0.25
Nodes (7): CLAUDE.md — member-admin ("Mitglieder Management Portal"), Entwickeln (macOS/Windows), graphify, Neuer Chat — so einsteigen, Regeln für Änderungen, Verteilung / offene Punkte (Stand 2026-11-14), Was die App kann

### Community 7 - "Release_Notes.md"
Cohesion: 0.33
Nodes (5): Version 0.0.1, Version 0.0.2, Version 0.0.3, Version 0.1.0, Versionen 0.0.4 – 0.0.7

### Community 8 - "Mitglieder Management Portal"
Cohesion: 0.25
Nodes (7): Die Excel-Liste, Einstellungen (`config.ini`), Für Entwickler, Installation, Mitglieder Management Portal, Regeln der Berechnung, So geht es

### Community 12 - "version"
Cohesion: 0.22
Nodes (9): version, on, push, workflow_dispatch, branches, description, required, type (+1 more)

## Knowledge Gaps
- **5 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Members` connect `Members` to `pandas`, `main_window.py`, `test_regressions.py`, `MainWindow`?**
  _High betweenness centrality (0.098) - this node is a cross-community bridge._
- **Are the 3 inferred relationships involving `Members` (e.g. with `Member` and `MemberListTest`) actually correct?**
  _`Members` has 3 INFERRED edges - model-reasoned connections that need verification._
- **Should `with` be split into smaller, more focused modules?**
  _Cohesion score 0.05668016194331984 - nodes in this community are weakly interconnected._
- **Why does `MainWindow` connect `MainWindow` to `pandas`, `birthday_calculation.py`, `main_window.py`, `test_regressions.py`, `Members`, `ResultPage`?**
  _High betweenness centrality (0.095) - this node is a cross-community bridge._
- **Are the 8 inferred relationships involving `MainWindow` (e.g. with `UiTest` and `MemberListError`) actually correct?**
  _`MainWindow` has 8 INFERRED edges - model-reasoned connections that need verification._
- **Should `birthday_calculation.py` be split into smaller, more focused modules?**
  _Cohesion score 0.14112903225806453 - nodes in this community are weakly interconnected._
- **Why does `ResultPage` connect `ResultPage` to `birthday_calculation.py`, `main_window.py`, `MainWindow`?**
  _High betweenness centrality (0.057) - this node is a cross-community bridge._