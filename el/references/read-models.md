# Read models: reports, dashboards, activity

For a screen that reads more than it writes: a report, a chart, a dashboard, a period summary, an export, an activity or audit view. Integrity stays in backend.md (B6, B7, B40-B43) and screen rules in design.md (D10, D13-D15); this file is how they combine. A system that records more than it can show has an unfinished read side.

## Decide before building

| Question | Answer |
| --- | --- |
| Whose question is it | Name the reader and the decision they take with it. No reader, no report. |
| What composes each figure | Every figure is the sum of rows the reader can open. A total that cannot be opened is a defect. |
| Which period | Business time zone and period bounds have one domain owner; queries receive bounds as parameters. |
| What volume | Rows per period at the size the product must serve, and the budget for the first page and for each block. |
| Who may read | The permission that already reads the underlying facts, in the same scope. A new permission needs a reader the existing ones cannot describe. |

## The read side

1. **Aggregate where the data lives.** One statement per block returns rows already grouped, ordered, and filled for empty periods. Server code maps rows to the contract; the client draws. No summing, grouping, sorting, or gap-filling in a handler loop or in the browser.
2. **Ship data, not prose.** Exact figures in stated units; a state as a key (with its label and tone when the server owns the copy); a difference as its own type (balanced, short by an amount, over by an amount). Never a sign, a suffix, or a word that a consumer must parse out of a formatted string. Server-worded rows are for text that must print identically on several outputs.
3. **One selector per period.** Detail, day, and month read the same facts through the same predicate, so totals agree by construction. Prove it with a test: month equals the sum of its days equals the sum of its details.
4. **Comparison travels with the series.** The total and the same total for the previous equal period come from the server.
5. **A stored aggregate is the last remedy, in this order:** the index the plan needs; a query that starts from the small side; a row the database writes when a period closes and can no longer change; partitioning. Never a counter the application maintains, never a cache without an invalidation owner (B7, B43).
6. **Measure at volume** with the production role and a generic plan before the item closes (A24, B42); record the workload and the number.
7. **An export is the report's own rows:** the same query, bounded, safe against spreadsheet formulas, and recorded when the data is sensitive.

## Activity and audit views

- Actions are a closed set. Each has exactly one human sentence built from typed data, so adding an action without its wording fails a static check (the pattern of D29).
- Record who, acting as what, when, in which scope, about which object (kind and identifier), and the data of the sentence. Never a secret. Append-only by privilege, not by convention (B6).
- Index the three questions people ask: the tenant's timeline, one actor's, one object's.
- **"Not done" is derived, never stored.** Obligations that facts create (opened and not closed, sent and not received, flagged and not reviewed) come from one query and disappear when the settling fact is inserted. No task table, no "mark as done".

## Screen shape

- Summary that answers the question, then filters that live in the URL, then one table, then the drill-down. A chart sits above the table of the same data and a mark opens its rows; a chart without its table has not earned its place (D13).
- A few charts per page, one question each, stated in its title. Use the design system's chart primitives before adding a library (A15, D48).
- Exceptions first: rows that need attention are marked and reachable without scrolling.
- A period table lists every unit of the period, empty ones included; a missing day reads as missing data.

## Checks

- Totals reconcile across levels, by test.
- A reader limited to one scope sees only its rows at every level, exports included.
- First page and each block inside their budget at the target volume.
