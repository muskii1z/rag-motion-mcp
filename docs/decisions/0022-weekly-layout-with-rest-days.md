# 0022. Weekly layout with rest days, Monday start, 8 weeks
**Date:** 2026-10-08 · **Step:** M4 · **Status:** accepted

## Context
rag-motion programs have days ("Day 1", "Day 2") but never had dates. wger places a routine's days on the calendar in order. In the first live save, wger put three full-body days back to back (Thu, Fri, Sat), then restarted on Monday. Coach review: three full-body days in a row is poor programming.

## Options considered
- **Save only the training days, as wger orders them.** Pros: simplest. Cons: sessions land on consecutive days with no recovery.
- **Fill a 7-day week with training days on fixed weekdays and rest days between, starting next Monday.** Pros: spreads sessions the way a coach would (3 days -> Mon, Wed, Fri). Cons: fixed weekdays; the client can't choose which days.

## Decision
`WEEK_LAYOUT` sets the training weekdays for each number of sessions: 1: Mon; 2: Mon, Thu; 3: Mon, Wed, Fri; 4: Mon, Tue, Thu, Fri; 5: Mon, Tue, Wed, Fri, Sat; 6: Mon-Sat (7: every day). The other days become wger rest days. The routine starts next Monday (today if it is Monday) and runs 8 weeks.

## Tradeoffs
The client's own schedule is ignored (e.g. a client who can only train at weekends). The 8-week length is fixed and doesn't come from the program.

## Revisit when
A client needs specific training days, or rag-motion programs start to include a length or a schedule.
