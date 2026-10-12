# Waiting on you

The control board's "Waiting on you" box lists every line below that starts with `- `: the
decisions only the founder can make. Remove a line once it is ruled; with no line left the box is
hidden. Read by `tools/control_board/build_control_board.py` (`waiting_on_you`).

- Save FUTURE_security_requirements.md into docs/founder-inputs/: the queued step that records R21 (coach charter), the R19 and W8 amendments and T95-T97 as DRAFT / Won't-now reads it, and it is not on this machine
- G-157, a proposal for DEF-093 (not built — needs a ruling): a turn's time limits add up past 45 s and a stalled after-check discards a finished reply (run 121314: the grader's call hung, the 40 s wall cut the turn to a code-written reply, 50.4 s). Proposed: (1) one turn deadline — the route stamps the turn's start, and the executor's wall is the time left to 45 s minus a 3 s reserve for closing (never more than 40 s); (2) a request timeout on every judge call (judgment 10 s, coherence 8 s, grader 8 s) set on the model client — a judge that runs out is recorded 'not checked (time)' and the coach's finished reply is kept, never discarded; (3) the guard stays within 10.5 s (G-154). With these, the worst turn is guard 10.5 + judgment 10 + what is left of the wall, cut at 42 s, + 3 s closing = under 45 s. An ADR refining ADR-0043 / T70
