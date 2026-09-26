# Workspace — product requirements (DRAFT — founder, 2026-09-26)

> **Draft, not ratified.** Recorded verbatim; no feature cites it until the founder ratifies it.

Applies to all phases. Depends on R8 (login) wherever a "logged-in
person" is named; until R8, the case's Belt name is used.

W1 OVERVIEW PAGE — explain the method
   As a Belt or team member, I want an overview page that explains what
   Agent Improve is, the DMAIC method and each section of the workspace,
   with a tab per phase describing what the phase is for and what it must
   deliver, so that the team understands the journey before starting.
   Acceptance: each phase tab shows the phase's purpose and its required
   deliverables; the content comes from the same source as the coach
   (the phase skills / requirements), never typed twice.
   Today: partly exists (Phase overview tab, DMAIC tabs).
   Open: which language(s)? Who may edit the texts?

W2 PROJECT STATUS — where the project stands
   As a Belt, I want the overview page to show the project's current
   phase, its duration from day 1 to today, and what is next or waiting
   for completion, so that the team always knows where it stands.
   Acceptance: phase, day count, open elements and pending approvals are
   computed from the phase state; the same figures appear everywhere they
   are shown.
   Today: not built (sidebar shows field counts only).
   Open: show planned end date vs actual? Show time per phase?

W3 COACHING PAGE WELCOME — summary so far
   As a Belt, I want the coach to greet me by name and summarise what has
   been achieved so far, so that I can resume without re-reading history.
   Acceptance: the summary uses confirmed values from the phase state
   only — nothing invented; open elements are listed.
   Today: a generic "Welcome back" panel exists; no state-based summary.

W4 CHOOSE WHAT TO WORK ON NEXT
   As a Belt, I want to either pick any element not yet confirmed from a
   list, or accept the coach's recommended next element, so that the team
   can work in the order that suits its information.
   Acceptance: the list shows only unconfirmed elements; the recommended
   element is the one the coach will actually work on (never a different
   one — see G-107).
   Open: DESIGN DECISION NEEDED (ADR) — today code works the elements in a
   fixed order; free choice changes that. Which elements must stay in
   order (e.g. business case before benefits analysis)?

W5 UPLOADS STRENGTHEN ANSWERS
   As a Belt, I want to upload documents on the coaching page, so that the
   coach can use them to help me give better, more complete answers.
   Acceptance: the coach reads the upload, checks it against the current
   element's acceptance criteria, and asks for what is missing; nothing
   from an upload is stored until the Belt confirms it (§21).
   Today: upload exists; the coach cannot yet read an upload's content
   (G-82).
