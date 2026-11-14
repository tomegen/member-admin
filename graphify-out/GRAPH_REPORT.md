# Graph Report - member-admin  (2026-11-14)

## Corpus Check
- 18 files · ~4,183 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 3 file(s) not represented in the graph (top: (none) 1, .ini 1, .ico 1)

## Summary
- 128 nodes · 233 edges · 12 communities (7 shown, 5 thin omitted)
- Extraction: 93% EXTRACTED · 7% INFERRED · 0% AMBIGUOUS · INFERRED: 17 edges (avg confidence: 0.94)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `ecc449fb`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- with
- mitgliederverwaltung.py
- birthday_calculation.py
- version
- test_regressions.py
- Aufbau
- CLAUDE.md — member-admin ("Mitglieder Management Portal")
- Release_Notes.md
- member-admin
- .claude/CLAUDE.md
- Members
- Config

## God Nodes (most connected - your core abstractions)
1. `Members` - 15 edges
2. `MemberListTest` - 12 edges
3. `with` - 12 edges
4. `Config` - 10 edges
5. `shift_years()` - 10 edges
6. `CLAUDE.md — member-admin ("Mitglieder Management Portal")` - 10 edges
7. `is_birthday()` - 9 edges
8. `make_member()` - 9 edges
9. `Aufbau` - 9 edges
10. `Member` - 8 edges

## Surprising Connections (you probably didn't know these)
- `Aufbau` --references--> `is_birthday()`  [INFERRED]
  CLAUDE.md → logic/birthday_calculation.py
- `Festlegungen (2026-11-14 behoben, nicht rückgängig machen)` --references--> `MemberListError`  [INFERRED]
  CLAUDE.md → model/members.py
- `Aufbau` --references--> `StartPage`  [INFERRED]
  CLAUDE.md → ui/start_page.py
- `Aufbau` --references--> `Member`  [INFERRED]
  CLAUDE.md → model/member.py
- `Aufbau` --references--> `BirthdayPage`  [INFERRED]
  CLAUDE.md → ui/birthday_page.py

## Import Cycles
- None detected.

## Communities (12 total, 5 thin omitted)

### Community 0 - "with"
Cohesion: 0.11
Nodes (19): steps, GITHUB_TOKEN, env, id, name, run, uses, with (+11 more)

### Community 2 - "birthday_calculation.py"
Cohesion: 0.21
Nodes (6): is_birthday(), write_birthdays_into_ics(), write_birthdays_into_txt(), CalculationTest, LeapDayTest, make_member()

### Community 3 - "version"
Cohesion: 0.17
Nodes (11): runs-on, version, jobs, build, name, on, workflow_dispatch, description (+3 more)

### Community 5 - "Aufbau"
Cohesion: 0.39
Nodes (5): Aufbau, shift_years(), is_honor(), write_honors_into_txt(), HonorPage

### Community 6 - "CLAUDE.md — member-admin ("Mitglieder Management Portal")"
Cohesion: 0.22
Nodes (8): CLAUDE.md — member-admin ("Mitglieder Management Portal"), graphify, Lokal ausführen (macOS), Neuer Chat — so einsteigen, Offene Verbesserungen (Auswahl, Stand 2026-11-14), Regeln für Änderungen, Tests, Was das Tool kann

### Community 7 - "Release_Notes.md"
Cohesion: 0.50
Nodes (3): Version 0.0.1, Version 0.0.2, Version 0.0.3

### Community 10 - "Members"
Cohesion: 0.27
Nodes (4): Festlegungen (2026-11-14 behoben, nicht rückgängig machen), MemberListError, Members, MemberListTest

## Knowledge Gaps
- **5 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Aufbau` connect `Aufbau` to `mitgliederverwaltung.py`, `birthday_calculation.py`, `test_regressions.py`, `CLAUDE.md — member-admin ("Mitglieder Management Portal")`, `Config`?**
  _High betweenness centrality (0.102) - this node is a cross-community bridge._
- **Are the 2 inferred relationships involving `Members` (e.g. with `MemberAdminApp` and `MemberListTest`) actually correct?**
  _`Members` has 2 INFERRED edges - model-reasoned connections that need verification._
- **Should `with` be split into smaller, more focused modules?**
  _Cohesion score 0.10526315789473684 - nodes in this community are weakly interconnected._
- **Why does `CLAUDE.md — member-admin ("Mitglieder Management Portal")` connect `CLAUDE.md — member-admin ("Mitglieder Management Portal")` to `Members`, `Aufbau`?**
  _High betweenness centrality (0.085) - this node is a cross-community bridge._
- **Are the 3 inferred relationships involving `MemberListTest` (e.g. with `Config` and `MemberListError`) actually correct?**
  _`MemberListTest` has 3 INFERRED edges - model-reasoned connections that need verification._
- **Why does `Members` connect `Members` to `mitgliederverwaltung.py`, `Config`, `test_regressions.py`?**
  _High betweenness centrality (0.072) - this node is a cross-community bridge._
- **Are the 2 inferred relationships involving `Config` (e.g. with `MemberAdminApp` and `MemberListTest`) actually correct?**
  _`Config` has 2 INFERRED edges - model-reasoned connections that need verification._