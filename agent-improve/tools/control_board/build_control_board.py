#!/usr/bin/env python3
"""
Control board generator.
Steps, markers and stages come from the repo's generated board.html (DERIVED). The plan comes from
stories.py; the architecture text from arch_view.py; the component inventory from system_view.py.
  python3 build_control_board.py <board.html> <out.html>
"""
import sys, html as H, datetime, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).parent))
from parse_board import parse
TABS = [("vert", "The system")]
import system_view as sv
import stories, arch_view

e = H.escape
STATE = {"done":("g","built"),"now":("o","building now"),"ready":("b","ready"),
         "queued":("q","queued"),"blocked":("r","blocked"),"later":("q","queued"),
         "open":("o","building now"),"BUILT":("g","built"),
         "UNMEASURED":("d","unmeasured"),"DISPUTED":("a","landed, but disputed")}
VAR = {"g":"good","o":"warn","b":"accent","q":"pending","r":"bad","a":"warn","d":"bad"}



def integrity(d):
    """Does the board render everything it counts? Derived, not asserted."""
    expected_open = d["total"] - d["landed"]
    open_cards = len([x for x in d["steps"] if x["status"] != "done"])
    missing = expected_open - open_cards
    if missing <= 0: return ""
    return (f'<div class="note"><b>{missing} step(s) counted but rendered nowhere.</b> '
            f'The source board declares {d["landed"]} landed of {d["total"]}, so {expected_open} should '
            f'be open — it renders {open_cards}. This page can only show what the board draws, so those '
            f'{missing} are invisible here too. Until the generator fails closed on an out-of-band step, '
            f'a complete plan and an under-reporting board look identical.</div>')


def next_html(d, reg):
    """DERIVED — the top-ranked story that is not done, and its first open step.
    The decision is the RANK, made once in stories.py; which item is next follows from it."""
    st = stories.next_story()
    if st is None:
        return '<div class="nx"><div class="nx-k">NEXT — ONE THING</div><div class="nx-t">every ranked story is done</div></div>'
    task = next((t for t in st["tasks"] if t[3] != "done"), None)
    step = {s["num"]: s for s in d["steps"]}.get(task[0], {}) if task else {}
    num = task[0] if task else st["id"]
    title = step.get("title") or (task[1] if task else st["title"])
    open_rows = [r for r in st["rows"] if not reg.get(r)]
    n = dict(
      who="%s &middot; rank %d &middot; %s" % (e(st["id"]), st["rank"], e(st["title"])),
      why="The top-ranked story that is not done. %d of its %d rows are still red in Appendix H."
          % (len(open_rows), len(st["rows"])) if st["rows"] else "The top-ranked story that is not done.",
      gives=("rows " + " ".join("#%d" % r for r in open_rows)) if open_rows else "no capability row yet",
      you=e(step.get("done_when") or step.get("precondition") or "—"))
    return (
      '<div class="nx">'
      '<div class="nx-k">NEXT — ONE THING &middot; <b>DERIVED</b></div>'
      '<div class="nx-t"><b>%s</b> &nbsp;%s</div>'
      '<div class="nx-g">'
        '<div><span>THE STORY</span>%s</div>'
        '<div><span>WHY IT IS NEXT</span>%s</div>'
        '<div><span>WHAT IT GIVES YOU</span>%s</div>'
        '<div><span>DONE WHEN</span>%s</div>'
      '</div></div>'
      '<div class="orient"><b>Read it in three passes.</b> The bands above say how far off the end is, using the procedure’s own grouping. The columns below are the system, left to right in the order a turn travels it — each carrying what exists, the architecture markers still open, and the steps that own them. Underneath: what the frameworks actually say, and the findings that are real and not yet carded.</div>'
    ) % (e(num), e(title), n["who"], e(n["why"]), e(n["gives"]), n["you"])


AST={"b":("#2F6B3C","#EAF1EA","#CBDECD","built"),
     "p":("#8A6A1E","#FBF3E2","#E7D5A8","stands in"),
     "a":("#6E6959","#F0EEE7","#DCD6C6","absent"),
     "u":("#4A5A7A","#ECEFF6","#C9D2E4","not knowable")}

CHIP = {"b":("#2F6B3C","#EAF1EA","#CBDECD"),"p":("#8A6A1E","#FBF3E2","#E7D5A8"),
        "a":("#6E6959","#F0EEE7","#DCD6C6"),"c":("#A8201A","#FBECEB","#E9C0BC"),
        "u":("#4A5A7A","#ECEFF6","#C9D2E4")}

JST = {
 "hot":   ("var(--bad)",     "var(--bad-soft)",     "blocks other work \u2014 do first"),
 "ready": ("var(--good)",    "var(--good-soft)",    "specified and buildable"),
 "spec":  ("var(--warn)",    "var(--warn-soft)",    "waiting on a decision or a document from you"),
 "later": ("var(--pending)", "var(--pending-soft)", "real, and not blocking a Belt finishing Define"),
}
JSTAGE = {"one":"STAGE ONE","two":"STAGE TWO","three":"STAGE THREE"}

ZKEY = {"UI":"UI","SUP":"SUP","PHASE":"PHASE","COACH":"COACH","GATE":"GATE",
        "STORE":"STORE","OPS":"OPS"}
SCLS = {"done":"g","ready":"b","building":"o","queued":"q","blocked":"r"}

def _zone_of(step):
    z = (step.get("zone") or "").split("\u00b7")[0].strip()
    return z or "OPS"

TST = {"done": ("DONE", "var(--good)", "var(--good-soft)"),
       "now": ("IN PROGRESS", "var(--warn)", "var(--warn-soft)"),
       "next": ("NEXT", "var(--accent)", "var(--accent-soft)"),
       "todo": ("TO DO", "var(--pending)", "var(--pending-soft)"),
       "blocked": ("BLOCKED", "var(--bad)", "var(--bad-soft)"),
       "backlog": ("BACKLOG", "var(--pending)", "var(--pending-soft)")}

HAND = ('<span class="hand" title="typed in stories.py: no derivable source for this status">'
        '&nbsp;HAND</span>')


def stories_html(reg):
    """Epic > Story > Task / Bug. The single place the work lives.
    Rows proven are COUNTED IN APPENDIX H, not summed from the stories that claim them."""
    allst = [x for ep in stories.EPICS for x in ep["stories"]]
    proven = sum(1 for g in reg.values() if g)
    total = len(reg)
    o = ['<div class="sto"><div class="ms-h">THE WORK &mdash; epics, stories, tasks and bugs</div>',
         '<p class="blurb" style="max-width:112ch">A <b>story</b> says what the Belt needs, in their words. '
         'Its acceptance is one or more capability rows; it is done when their checks pass. A <b>task</b> is the '
         'engineering that delivers it: a procedure step. A <b>bug</b> is something built that is wrong. The '
         '<b>rank</b> number is the one order open stories are worked in. Rank 1 is what is happening now.</p>',
         '<div class="capbar"><div class="capnum">%d <span>of %d capability rows proven</span></div>'
         '<div class="bar" style="flex:1"><i style="width:%d%%"></i></div></div>' % (proven, total, int(100*proven/total))]
    ranked = sorted([x for x in allst if x["rank"]], key=lambda x: x["rank"])
    o.append('<div class="rkstrip"><span class="rkh">THE ORDER</span>')
    for x in ranked:
        lab, fg, bg = TST[x["status"]]
        o.append('<span class="rki" style="border-color:%s;background:%s"><b>%d</b> %s &middot; %s</span>'
                 % (fg, bg, x["rank"], e(x["id"]), e(x["title"][:58] + ("\u2026" if len(x["title"]) > 58 else ""))))
    o.append('</div>')
    for ep in stories.EPICS:
        sts = ep["stories"]; dn = sum(1 for x in sts if x["status"] == "done")
        o.append('<div class="epc"><div class="eph"><span class="epid">%s</span><b>%s</b>'
                 '<span class="epn">%d of %d stories done</span></div><div class="epw">%s</div>'
                 % (e(ep["id"]), e(ep["title"]), dn, len(sts), e(ep["why"])))
        o.append('<div class="stgrid">')
        for x in sts:
            lab, fg, bg = TST[x["status"]]
            rank = ('<span class="rk">%d</span>' % x["rank"]) if x["rank"] else '<span class="rk nr">&middot;</span>'
            rows = ("rows " + " ".join("#%d" % r for r in x["rows"])) if x["rows"] else "none yet"
            o.append('<div class="stc %s" style="border-top-color:%s">' % (x["status"], fg))
            o.append('<div class="sth">%s<span class="sid">%s</span><span class="sst" style="color:%s;background:%s">%s%s</span></div>'
                     % (rank, e(x["id"]), fg, bg, lab, HAND if x["src"] == "hand" else ""))
            o.append('<div class="stt">%s</div><div class="sta">&ldquo;%s&rdquo;</div>' % (e(x["title"]), e(x["ask"])))
            o.append('<div class="stm"><span>ACCEPTANCE</span> %s &nbsp; <span>WHERE</span> %s</div>'
                     % (e(rows), e(" \u00b7 ".join(x["comps"]))))
            for code, t, comp, st, src in x["tasks"]:
                l2, f2, b2 = TST[st]
                o.append('<div class="tkr"><span class="tkt">TASK</span>'
                         '<span class="tkx"><b class="tkc">%s</b> %s<span class="tkp">%s</span></span>'
                         '<span class="tks" style="color:%s;background:%s">%s%s</span></div>'
                         % (e(code), e(t), e(comp), f2, b2, l2, HAND if src == "hand" else ""))
            for t, comp, st, where in x["bugs"]:
                l2, f2, b2 = TST[st]
                o.append('<div class="tkr bug"><span class="tkt">BUG</span>'
                         '<span class="tkx">%s<span class="tkp">%s &middot; found at %s</span></span>'
                         '<span class="tks" style="color:%s;background:%s">%s%s</span></div>'
                         % (e(t), e(comp), e(where), f2, b2, l2, HAND))
            if x.get("note"):
                o.append('<div class="stn">%s</div>' % e(x["note"]))
            o.append('</div>')
        o.append('</div></div>')
    o.append('<div class="uns"><div class="ms-h">NOT YET A STORY &mdash; findings with no user-visible outcome</div><ul class="alist">')
    for t, n in stories.UNSTORIED:
        o.append('<li><b>%s</b> &mdash; %s</li>' % (e(t), e(n)))
    o.append('</ul></div></div>')
    return "".join(o)

def stages_html(d):
    """The procedure's ten stages, derived from step numbers. Shows where we are."""
    import collections
    g = collections.defaultdict(lambda: {"done": 0, "n": 0})
    for num, st in d["all_steps"].items():
        k = num.split(".")[0]
        g[k]["n"] += 1
        if st["status"] == "done": g[k]["done"] += 1
    keys = sorted(g, key=lambda x: int(x))
    here = next((k for k in keys if g[k]["done"] < g[k]["n"]), keys[-1])
    o = ['<div class="stg"><div class="ms-h">THE PROCEDURE\u2019S STAGES &mdash; where the whole '
         'refactor stands. DERIVED from the step register.</div>',
         '<p class="blurb">%s</p>' % e(sv.STAGE_NOTE), '<div class="stgrow">']
    for k in keys:
        v = g[k]; pct = int(100 * v["done"] / v["n"]) if v["n"] else 0
        name, gloss, quoted = sv.STAGES.get(k, ("stage " + k, "", False))
        state = "g" if pct == 100 else ("o" if k == here else "q")
        o.append('<div class="stgi %s%s">' % (state, " now" if k == here else ""))
        if k == here: o.append('<div class="stghere">YOU ARE HERE</div>')
        o.append('<div class="stgn"><b>%s</b> %s%s</div>' % (e(k), e(name),
                 ' <em>named in the document</em>' if quoted else ''))
        o.append('<div class="ms-b"><i style="width:%d%%"></i></div>' % pct)
        o.append('<div class="ms-c">%d of %d</div><div class="stgg">%s</div></div>'
                 % (v["done"], v["n"], e(gloss)))
    o.append('</div></div>')
    return "".join(o)

def spec_html(key):
    """The architecture for this column: state fields, node conditions and the
    exceptions still open. RELAYED from the tree audit at 208e4a7."""
    cfg = sv.SPEC.get(key)
    if not cfg: return ""
    o = ['<div class="vsec">THE ARCHITECTURE HERE &middot; <b>RELAYED</b></div>']
    lvl = cfg.get("level")
    if lvl:
        L = getattr(arch_view, lvl)
        o.append('<div class="spb"><div class="spt">%s</div>' % e(L["state"]["title"]))
        for fname, fdesc in L["state"]["fields"]:
            o.append('<div class="spf"><code>%s</code><span>%s</span></div>' % (e(fname), e(fdesc)))
        o.append('</div>')
        o.append('<div class="spb"><div class="spt">Conditions</div>')
        for c in L["conditions"]:
            o.append('<div class="spl">%s</div>' % e(c))
        o.append('</div>')
        if L["exceptions"]:
            o.append('<div class="spb"><div class="spt">Exceptions &mdash; still open</div>')
            for st, txt, step in L["exceptions"]:
                fg, bg, bd = CHIP[st]
                o.append('<div class="spl ex" style="border-color:%s">%s%s</div>'
                         % (fg, e(txt), (' <b style="color:%s">%s</b>' % (fg, e(step))) if step else ''))
            o.append('</div>')
    for nm in cfg.get("nodes", []):
        n = next((x for x in arch_view.NODES if x["name"] == nm), None)
        if not n: continue
        o.append('<div class="spb"><div class="spt">%s%s</div><div class="spo">%s</div>'
                 % (e(n["name"]), ' <em>THE AGENT</em>' if n.get("agent") else '', e(n["one"])))
        for w in n["what"]:  o.append('<div class="spl">%s</div>' % e(w))
        for c in n["cond"]:  o.append('<div class="spl cond">%s</div>' % e(c))
        for st, txt, step in n["exc"]:
            fg, bg, bd = CHIP[st]
            o.append('<div class="spl ex" style="border-color:%s">%s%s</div>'
                     % (fg, e(txt), (' <b style="color:%s">%s</b>' % (fg, e(step))) if step else ''))
        o.append('</div>')
    if cfg.get("middleware"):
        o.append('<div class="spb"><div class="spt">The eight middleware positions, in order</div>')
        for i, nm, st, txt, step in arch_view.MIDDLEWARE:
            fg, bg, bd = CHIP[st]
            o.append('<div class="spf"><code>%d %s</code><span>%s%s</span></div>'
                     % (i, e(nm), e(txt), (' <b style="color:%s">%s</b>' % (fg, e(step))) if step else ''))
        o.append('</div>')
    if cfg.get("validation"):
        o.append('<div class="spb"><div class="spt">The four validation layers</div>')
        for lid, nm, st, when, txt, step in arch_view.VALIDATION:
            fg, bg, bd = CHIP[st]
            o.append('<div class="spf"><code>%s %s</code><span>%s &middot; %s%s</span></div>'
                     % (e(lid), e(nm), e(when), e(txt),
                        (' <b style="color:%s">%s</b>' % (fg, e(step))) if step else ''))
        o.append('</div>')
    if cfg.get("tools"):
        o.append('<div class="spb"><div class="spt">Tools bound to Define</div><div class="atags">')
        for nm, st in arch_view.TOOLS["bound"]:
            o.append('<code>%s</code>' % e(nm))
        o.append('</div>')
        for nm, why, step in arch_view.TOOLS["absent"]:
            o.append('<div class="spl ex" style="border-color:var(--bad)"><code>%s</code> &mdash; %s%s</div>'
                     % (e(nm), e(why), (' <b>%s</b>' % e(step)) if step else ''))
        o.append('</div>')
    if cfg.get("stores"):
        o.append('<div class="spb"><div class="spt">The stores</div>')
        for nm, st, what, cond, step in arch_view.STORES:
            fg, bg, bd = CHIP[st]
            o.append('<div class="spf"><code style="color:%s">%s</code><span>%s%s%s</span></div>'
                     % (fg, e(nm), e(what), (' ' + e(cond)) if cond else '',
                        (' <b style="color:%s">%s</b>' % (fg, e(step))) if step else ''))
        o.append('</div>')
    if cfg.get("phases"):
        o.append('<div class="spb"><div class="spt">The five phases on one class</div>')
        for nm, nf, ng, st, script, tiers in arch_view.PHASES:
            fg, bg, bd = CHIP[st]
            o.append('<div class="spf"><code style="color:%s">%s</code>'
                     '<span>%d fields &middot; %d gate-required &middot; script: %s &middot; %s</span></div>'
                     % (fg, e(nm), nf, ng, e(script), e(tiers)))
        o.append('</div>')
    return "".join(o)


def full_diagram():
    """The whole system in one picture: browser, routes, supervisor, the phase
    subgraph with its middleware and tools, the stores and indexes, and the
    external services. Status is the audit's (RELAYED, 208e4a7)."""
    W, H = 1720, 1460
    C = {"b": ("#1F7A52", "#E4F4EC", "#B4DCC6"),
         "p": ("#A96C12", "#FDF2DF", "#EBD3A4"),
         "a": ("#B0332F", "#FCE8E7", "#EFBFBC"),
         "n": ("#2A3640", "#FFFFFF", "#CFD8E0"),
         "x": ("#1F4D8C", "#E6EFF9", "#BBD2EC")}
    P = ['<svg viewBox="0 0 %d %d" xmlns="http://www.w3.org/2000/svg" class="dsvg">' % (W, H),
         '<defs><marker id="fa" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" '
         'orient="auto-start-reverse"><path d="M0 0L10 5L0 10z" fill="#7C8894"/></marker>'
         '<marker id="fb" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" '
         'orient="auto-start-reverse"><path d="M0 0L10 5L0 10z" fill="#B0332F"/></marker></defs>',
         '<rect width="%d" height="%d" fill="#FFFFFF"/>' % (W, H)]

    def band(y, h, label, note=""):
        P.append('<rect x="28" y="%d" width="%d" height="%d" rx="12" fill="#F7FAFC" stroke="#DCE4EB"/>'
                 % (y, W - 56, h))
        P.append('<text class="fbl" x="48" y="%d">%s</text>' % (y + 26, label))
        if note:
            P.append('<text class="fbn" x="%d" y="%d" text-anchor="end">%s</text>' % (W - 48, y + 26, note))

    def bx(x, y, w, h, st, title, lines=(), tag=""):
        fg, bg, bd = C[st]
        P.append('<rect x="%d" y="%d" width="%d" height="%d" rx="9" fill="%s" stroke="%s" stroke-width="1.6"/>'
                 % (x, y, w, h, bg, bd))
        P.append('<text class="fbt" x="%d" y="%d" fill="%s">%s</text>' % (x + 13, y + 25, fg, title))
        for i, l in enumerate(lines):
            P.append('<text class="fbd" x="%d" y="%d">%s</text>' % (x + 13, y + 45 + i * 17, l))
        if tag:
            P.append('<text class="ftg" x="%d" y="%d" fill="%s" text-anchor="end">%s</text>'
                     % (x + w - 13, y + 25, fg, tag))

    def arrow(x1, y1, x2, y2, bad=False, label="", lx=0, ly=0, dash=False):
        d = ' stroke-dasharray="6 5"' if dash else ''
        P.append('<path d="M%d %d L%d %d" fill="none" stroke="%s" stroke-width="1.8"%s marker-end="url(#%s)"/>'
                 % (x1, y1, x2, y2, "#B0332F" if bad else "#7C8894", d, "fb" if bad else "fa"))
        if label:
            P.append('<text class="fed" x="%d" y="%d">%s</text>' % (lx, ly, label))

    # 1 — browser -----------------------------------------------------------
    band(28, 132, "1 · THE BROWSER — one HTML file", "what the Belt actually sees")
    for i, (st, t, l) in enumerate([
        ("b", "Case list", ["create · open"]),
        ("b", "Coaching screen", ["send a turn, read the reply"]),
        ("p", "Progress", ["26 old names · reads 0 of 26"]),
        ("b", "Upload evidence", ["file in, indexed"]),
        ("b", "Gate review panel", ["correct v2 rows, tier pills"]),
        ("a", "Gate screen", ["does not exist · 10.2"])]):
        bx(48 + i * 272, 66, 254, 80, st, t, l)

    # 2 — routes ------------------------------------------------------------
    band(192, 132, "2 · FASTAPI ROUTES", "the only writer to the case record today")
    for i, (st, t, l) in enumerate([
        ("b", "POST /ask", ["one turn, one graph run"]),
        ("b", "cases · upload · health", ["lifecycle"]),
        ("p", "GET /gate/review", ["calls assemble · 500s today"]),
        ("a", "POST /gate submit", ["builds from _validated · 6.42"]),
        ("a", "POST approve", ["no endpoint · 7.7"]),
        ("a", "/ask/stream", ["no streaming · 10.1"])]):
        bx(48 + i * 272, 230, 254, 80, st, t, l)
    arrow(175, 148, 175, 226, label="a turn", lx=190, ly=190)
    arrow(1355, 226, 1355, 148, label="the reply", lx=1180, ly=190)

    # 3 — supervisor --------------------------------------------------------
    band(356, 150, "3 · SUPERVISOR GRAPH", "no model call anywhere in it")
    bx(48, 394, 330, 96, "b", "SupervisorState", ["7 fields · case, phase, gates passed",
                                                   "never carries captured data"])
    bx(398, 394, 300, 96, "b", "Input mapper", ["reads the case record,", "builds the phase state"])
    bx(718, 394, 300, 96, "b", "Phase node", ["invokes the subgraph", "with the inherited config"])
    bx(1038, 394, 330, 96, "a", "Output mapper", ["BUILT AND NOT CALLED — by ruling",
                                                   "so the route writes instead · 6.48"], tag="6.48")
    bx(1388, 394, 284, 96, "b", "Checkpointer", ["blob-backed, on the parent", "the child inherits it"])
    arrow(175, 314, 175, 390)

    # 4 — the phase subgraph ------------------------------------------------
    band(530, 430, "4 · PHASE SUBGRAPH — one class, five phases",
         "PhaseState · 23 fields · rebuilt from the record every turn")
    bx(48, 580, 300, 104, "p", "Planner", ["a model call, not an agent",
                                            "routes on a TURN COUNTER · 6.45"], tag="6.45")
    fg, bg, bd = C["p"]
    P.append('<rect x="378" y="562" width="740" height="330" rx="12" fill="#FFF8EC" stroke="#EBD3A4" stroke-width="2"/>')
    P.append('<text class="fbh" x="398" y="592" fill="#A96C12">Executor — THIS is the agent</text>')
    P.append('<text class="fbd" x="398" y="614">the model, its tools, and eight middleware wrapped around it</text>')
    P.append('<text class="fsl" x="398" y="646">BEFORE THE MODEL</text>')
    for i, (st, t) in enumerate([("b", "1 state injection"), ("p", "2 skills — optional"),
                                 ("b", "3 summarise")]):
        f2, b2, d2 = C[st]
        P.append('<rect x="%d" y="656" width="220" height="30" rx="15" fill="%s" stroke="%s"/>' % (398 + i * 232, b2, d2))
        P.append('<text class="fch" x="%d" y="676" fill="%s">%s</text>' % (408 + i * 232, f2, t))
    P.append('<text class="fsl" x="398" y="716">THE MODEL CALL · structured output, 8 declared fields</text>')
    P.append('<text class="fsl" x="398" y="746">AFTER THE MODEL</text>')
    for i, (st, t) in enumerate([("b", "4 model retry"), ("b", "5 tool retry"), ("b", "6 coaching grader")]):
        f2, b2, d2 = C[st]
        P.append('<rect x="%d" y="756" width="220" height="30" rx="15" fill="%s" stroke="%s"/>' % (398 + i * 232, b2, d2))
        P.append('<text class="fch" x="%d" y="776" fill="%s">%s</text>' % (408 + i * 232, f2, t))
    for i, (st, t) in enumerate([("b", "7 coherence 2a"), ("p", "8 contradiction — inert"),
                                 ("a", "capture is untyped · CO-1")]):
        f2, b2, d2 = C[st]
        P.append('<rect x="%d" y="794" width="220" height="30" rx="15" fill="%s" stroke="%s"/>' % (398 + i * 232, b2, d2))
        P.append('<text class="fch" x="%d" y="814" fill="%s">%s</text>' % (408 + i * 232, f2, t))
    P.append('<text class="fsl" x="398" y="854">TOOLS BOUND · 7</text>')
    for i, t in enumerate(["rag × 3", "propose_template", "propose_diagram", "load_series", "savings"]):
        P.append('<rect x="%d" y="862" width="134" height="24" rx="12" fill="#E4F4EC" stroke="#B4DCC6"/>' % (398 + i * 142))
        P.append('<text class="fch" x="%d" y="879" fill="#1F7A52">%s</text>' % (406 + i * 142, t))
    bx(1148, 580, 262, 104, "p", "Validation stack", ["2a every turn · 2b at the gate",
                                                       "2c and 2d absent · 7.1 · 7.2"], tag="7.1 7.2")
    bx(1148, 700, 262, 92, "p", "Gate review", ["logs and passes through",
                                                 "no pause anywhere · 7.3"], tag="7.3")
    bx(1148, 806, 262, 86, "a", "Gate apply", ["applies nothing · 6.42"], tag="6.42")
    bx(1430, 580, 242, 104, "a", "read_artefact", ["the coach cannot read", "an upload · 6.43"], tag="6.43")
    bx(1430, 700, 242, 92, "a", "check_gate_status", ["no live gate preview"])
    bx(1430, 806, 242, 86, "a", "request_approval", ["six universal, not eight"])
    arrow(348, 632, 374, 632)
    arrow(1118, 632, 1144, 632)
    arrow(1279, 688, 1279, 696)
    arrow(1279, 794, 1279, 802)
    arrow(600, 490, 600, 558, label="the whole state, rebuilt", lx=615, ly=530)

    # 5 — storage -----------------------------------------------------------
    band(980, 150, "5 · STORAGE AND INDEXES", "Azure Blob and Azure AI Search")
    for i, (st, t, l) in enumerate([
        ("b", "Case record", ["cases/{id}.json — fields,", "change log, citations, uploads"]),
        ("p", "Checkpoints", ["written after each node;", "mid-node writes are a no-op · 6.47"]),
        ("b", "Evidence index", ["uploads, chunked, 12 fields"]),
        ("a", "Knowledge index", ["schema exists, nothing", "ingested · 9.0"]),
        ("a", "Case index", ["prior cases · 9.1"]),
        ("a", "Gate doc in the Store", ["what Measure reads — written", "by the mapper that never fires"])]):
        bx(48 + i * 272, 1018, 254, 96, st, t, l)
    arrow(140, 316, 140, 1012, dash=True, label="", lx=0, ly=0)
    P.append('<text class="fed" x="150" y="960">the route writes the record \u2014 AFTER the graph has returned</text>')
    arrow(1000, 896, 1000, 1014, label="nothing is written here during the turn", lx=1015, ly=960)

    # 6 — external ----------------------------------------------------------
    band(1148, 128, "6 · EXTERNAL SERVICES", "outside the application")
    for i, (t, l) in enumerate([
        ("Azure OpenAI · chat", "every model call — coach, planner, graders"),
        ("Azure OpenAI · embeddings", "indexing and retrieval"),
        ("Azure AI Search", "three indexes, one populated"),
        ("Azure Blob Storage", "case records and checkpoints · no version on the write · 6.48")]):
        bx(48 + i * 412, 1184, 394, 74, "x", t, [l])
    P.append('<text class="fed" x="398" y="905">every model call in the picture above goes to Azure OpenAI, below</text>')

    P.append('<line x1="48" y1="1300" x2="%d" y2="1300" stroke="#DCE4EB"/>' % (W - 48))
    P.append('<text class="ffoot" x="48" y="1332">Read it top to bottom and the shape of the problem is visible: '
             'the browser and the routes are nearly complete, the graph is complete except for what decides and '
             'what stops,</text>')
    P.append('<text class="ffoot" x="48" y="1358">and the write to storage happens OUTSIDE the graph — which is '
             'why a second writer, a version on the write, and a resumable pause all keep returning as one problem.</text>')
    P.append('<text class="ffootd" x="48" y="1396">Green built · amber a stand-in that says so · red absent · '
             'blue external. Step numbers name the card that closes each gap. RELAYED from the tree audit at 208e4a7 '
             'and the reports at 62d7f17.</text>')
    P.append('</svg>')
    return "".join(P)

def system_html(d):
    o = []
    o.append('<p class="blurb" style="max-width:112ch"><b>One page.</b> Columns are the zones the step '
             'register itself assigns, left to right in the order a turn travels them &mdash; so reading '
             'across is the Belt\u2019s journey and reading down a column is one part of the system, end to '
             'end. Each column carries what is there, every OPEN architecture marker with the step that '
             'owns it, and every carded step in that zone.</p>')
    o.append('<p class="blurb" style="color:var(--ink-faint)">Source: %s. Marker states are the '
             'architecture\u2019s own &mdash; <b>&#9888;</b> built with a known defect, <b>&#9744;</b> not '
             'built. Provenance is marked on every block: DERIVED from the documents, RELAYED from Claude '
             'Code\u2019s tree audits, VERIFIED by me against a named source on a named date.</p>'
             % e(sv.SOURCE))
    o.append('<h4 class="sec">The shape of it &mdash; browser to storage, everything in one picture</h4>')
    o.append('<div class="ddiag">%s</div>' % full_diagram())
    cov = [0, 0]
    o.append('<h4 class="sec">The system, column by column</h4>')
    o.append('<!--COVERAGE-->')
    o.append('<div class="vcols">')
    for c in sv.COLUMNS:
        cards = [s for s in d["steps"] if _zone_of(s) == c["key"] and s["status"] != "done"]
        landed = [s for s in d["steps"] if _zone_of(s) == c["key"] and s["status"] == "done"]
        nm = sum(len(g[1]) for g in c["groups"])
        un = sum(1 for g in c["groups"] for m in g[1] if m[2] == "\u2014")
        o.append('<div class="vcol"><div class="vch"><b>%s</b><span class="vcz">%s</span>'
                 '<span class="vcw">%s</span></div>' % (e(c["label"]), e(c["sub"]), e(c["when"])))

        o.append('<div class="vsec">WHAT IS THERE &middot; %d &middot; <b>RELAYED</b></div><div class="jchips">'
                 % len(c["have"]))
        for st, txt in c["have"]:
            fg, bg, bd = CHIP[st]
            sid = stories.story_for_chip(txt) if st != "b" else None
            if st != "b":
                cov[0] += 1; cov[1] += 1 if sid else 0
            tag = ('<b class="sid2">%s</b>' % sid) if sid else ('<b class="sid2 no">NO STORY</b>' if st != "b" else '')
            o.append('<span class="achip" style="background:%s;border-color:%s;color:%s">'
                     '<i style="background:%s"></i>%s%s</span>' % (bg, bd, fg, fg, e(txt), tag))
        o.append('</div>')

        o.append(spec_html(c["key"]))
        o.append('<div class="vsec">OPEN MARKERS &middot; %d%s &middot; <b>DERIVED</b></div>'
                 % (nm, (' &middot; <b style="color:var(--bad)">%d unowned</b>' % un) if un else ''))
        if not nm:
            o.append('<div class="vclean">&#10003; %s</div>' % e(c.get("clean", "none")))
        for gname, ms in c["groups"]:
            if not ms:
                continue
            if len(c["groups"]) > 1:
                o.append('<div class="vgn">%s</div>' % e(gname))
            for st, sec, own in ms:
                unowned = own == "\u2014"
                sid = stories.story_for_marker(sec, own)
                cov[0] += 1; cov[1] += 1 if sid else 0
                tag = ('<b class="sid2">%s</b>' % sid) if sid else '<b class="sid2 no">NO STORY</b>'
                o.append('<div class="vm%s"><span class="vmi">%s</span>'
                         '<span class="vmt">%s %s<span class="vmo">%s</span></span></div>'
                         % (" un" if unowned else "", "&#9888;" if st == "w" else "&#9744;",
                            e(sec), tag, "no step owns this" if unowned else "step " + e(own)))

        o.append('<div class="vsec">OPEN STEPS &middot; %d &middot; <b>DERIVED</b></div>' % len(cards))
        if not cards:
            o.append('<div class="vclean">&#10003; nothing open in this zone</div>')
        sidx = stories.step_index()
        for st in sorted(cards, key=lambda x: (x["band"], x["num"])):
            cl = SCLS.get(st["status"], "q")
            sid = sidx.get(st["num"])
            cov[0] += 1; cov[1] += 1 if sid else 0
            pre = st["precondition"].replace("**", "")
            pre = pre.split(".")[0][:74]
            o.append('<div class="vcd c-%s"><span class="jc">%s</span><span class="jt">%s %s'
                     '<span class="jm">%s &middot; %s%s</span></span></div>'
                     % (cl, e(st["num"]), e(st["title"][:96]),
                        ('<b class="sid2">%s</b>' % sid) if sid else '<b class="sid2 no">NO STORY</b>',
                        e(st["status"].upper()), e(st["band"]), (" &middot; " + e(pre)) if pre else ""))
        if landed:
            o.append('<div class="vsec">LANDED &middot; %d</div><div class="vland">%s</div>'
                     % (len(landed), " &nbsp;".join("<b>%s</b>" % e(s["num"]) for s in landed)))
        o.append('</div>')
    o.append('</div>')

    banner = ('<div class="covb%s"><b>%d of %d</b> problems on this map belong to a story. '
              'Every amber or red component, every open architecture marker and every open step carries the '
              'ID of the story that fixes it; anything that does not says <b>NO STORY</b>.</div>'
              % ("" if cov[0] == cov[1] else " gap", cov[1], cov[0]))
    o = [x.replace('<!--COVERAGE-->', banner) for x in o]
    o.append('<h4 class="sec">What the frameworks say &mdash; VERIFIED by me at the named source, 23 Sep 2026</h4>')
    o.append('<p class="blurb">The only check nobody was running: the tree against the documentation of the '
             'libraries it is built on. Each line below is quoted, not paraphrased.</p><div class="fwk">')
    for quote, why, step, url in sv.FRAMEWORK:
        o.append('<div class="fw"><div class="fwq">%s</div><div class="fwy">%s</div>'
                 '<div class="fwm"><b>step %s</b> &middot; %s</div></div>'
                 % (e(quote), e(why), e(step), e(url)))
    o.append('</div>')

    if False:
      o.append('<h4 class="sec">Real, and not carded</h4>')
    pass
    return "".join(o)

def build(board_path, out_path):
    d = parse(board_path)
    idx = {s["num"]: s for s in d["steps"]}
    for s in d["vertical"]: idx.setdefault(s["num"], s)
    now = datetime.datetime.now().strftime("%d %b %Y, %H:%M")
    findings = []
    reg, _ = stories.resolve()
    sha, subject = stories.derived.built_from()
    NEXT_HTML = next_html(d, reg)
    BANDS_HTML = stages_html(d) + stories_html(reg)

    INTEGRITY_HTML = integrity(d)
    P=[]; a=P.append
    a(f'''<title>Control Board</title>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:wght@400;500;600;700&family=IBM+Plex+Mono:wght@400;500;600&display=swap">
<style>
:root{{--bg:#FFFFFF;--surface:#FFFFFF;--surface-2:#F2F6FA;--ink:#0B1219;--ink-dim:#3E4C57;--ink-faint:#6A7883;
--accent:#1F4D8C;--accent-soft:#E6EFF9;--accent-ink:#153A6C;--good:#1F7A52;--good-soft:#E4F4EC;--warn:#A96C12;
--warn-soft:#FDF2DF;--bad:#B0332F;--bad-soft:#FCE8E7;--pending:#7A858F;--pending-soft:#F1F5F8;--rule:#DCE4EB;
--fd:'IBM Plex Sans',system-ui,sans-serif;--fm:'IBM Plex Mono',Consolas,monospace;}}
@media (prefers-color-scheme:dark){{:root:not([data-theme="light"]){{--bg:#0F161F;--surface:#161F29;--surface-2:#1E2932;
--ink:#E7ECF1;--ink-dim:#98A5B1;--ink-faint:#67737E;--accent:#7CA3D1;--accent-soft:#223349;--accent-ink:#AEC8E7;
--good:#4FAE86;--good-soft:#173226;--warn:#D69A44;--warn-soft:#332711;--bad:#D9716A;--bad-soft:#33191A;
--pending:#7C8794;--pending-soft:#232B33;--rule:#2A3641;}}}}
:root[data-theme="dark"]{{--bg:#0F161F;--surface:#161F29;--surface-2:#1E2932;--ink:#E7ECF1;--ink-dim:#98A5B1;
--ink-faint:#67737E;--accent:#7CA3D1;--accent-soft:#223349;--accent-ink:#AEC8E7;--good:#4FAE86;--good-soft:#173226;
--warn:#D69A44;--warn-soft:#332711;--bad:#D9716A;--bad-soft:#33191A;--pending:#7C8794;--pending-soft:#232B33;--rule:#2A3641;}}
*{{box-sizing:border-box;}}
body{{margin:0;background:var(--bg);color:var(--ink);font-family:var(--fd);font-size:15px;padding:0 18px;padding-block:26px 56px;}}
.wrap{{max-width:min(2400px,97vw);margin:0 auto;}}
.eyebrow{{font-family:var(--fm);font-size:11px;letter-spacing:.09em;text-transform:uppercase;color:var(--accent);font-weight:500;}}
h1{{font-size:clamp(26px,4vw,36px);line-height:1.08;margin:8px 0 10px;font-weight:650;letter-spacing:-.01em;}}
.built{{font-family:var(--fm);font-size:11px;color:var(--ink);line-height:1.6;border:1px solid var(--warn);background:var(--warn-soft);border-radius:6px;padding:8px 12px;margin:10px 0 8px}}
.prov{{font-family:var(--fm);font-size:10.5px;color:var(--ink-faint);line-height:1.75;border:1px solid var(--rule);
border-left:3px solid var(--accent);border-radius:0 6px 6px 0;background:var(--surface);padding:10px 13px;margin:14px 0 18px;}}
.prov b{{color:var(--ink-dim);font-weight:500;}}
.sum{{display:flex;gap:16px;align-items:baseline;flex-wrap:wrap;margin-bottom:8px;}}
.sum .big{{font-family:var(--fm);font-size:24px;font-weight:600;font-variant-numeric:tabular-nums;}}
.sum .s{{font-size:11.5px;color:var(--ink-dim);}}
.bar{{height:8px;border-radius:4px;background:var(--pending-soft);overflow:hidden;}}
.bar i{{display:block;height:100%;background:var(--good);}}
.tabs{{display:flex;gap:2px;margin-top:24px;border-bottom:1px solid var(--rule);overflow-x:auto;}}
.tab{{font-family:var(--fm);font-size:12px;color:var(--ink-dim);background:none;border:none;cursor:pointer;
padding:9px 14px 11px;white-space:nowrap;border-bottom:2px solid transparent;margin-bottom:-1px;}}
.tab[aria-selected="true"]{{color:var(--accent);border-bottom-color:var(--accent);font-weight:500;}}






.fbl{{font:700 13px var(--fm);fill:#1F4D8C;letter-spacing:.1em}}
.fbn{{font:400 12.5px var(--fd);fill:#6A7883}}
.fbt{{font:600 15px var(--fd)}}
.fbh{{font:700 19px var(--fd)}}
.fbd{{font:400 12.5px var(--fd);fill:#3E4C57}}
.ftg{{font:600 11px var(--fm)}}
.fch{{font:600 11.5px var(--fm)}}
.fsl{{font:700 10.5px var(--fm);fill:#6A7883;letter-spacing:.09em}}
.fed{{font:400 12px var(--fd);fill:#6A7883}}
.ffoot{{font:600 14.5px var(--fd);fill:#0B1219}}
.ffootd{{font:400 12.5px var(--fd);fill:#6A7883}}
.spb{{border:1px solid var(--rule);border-radius:7px;background:var(--bg);padding:9px 10px;margin-bottom:7px;}}
.spt{{font:600 13px var(--fd);margin-bottom:6px;}}
.spt em{{font:600 9px var(--fm);color:var(--warn);font-style:normal;letter-spacing:.08em;margin-left:6px;}}
.spo{{font-size:12.5px;color:var(--ink-dim);margin-bottom:6px;line-height:1.4;}}
.spf{{display:flex;gap:8px;font-size:12.2px;line-height:1.4;padding:2px 0;}}
.spf code{{font-family:var(--fm);font-size:10px;color:var(--accent-ink);flex:0 0 108px;word-break:break-word;}}
.spf span{{color:var(--ink-dim);}}
.spl{{font-size:12.2px;line-height:1.45;color:var(--ink-dim);padding:3px 0 3px 9px;border-left:2px solid var(--rule);margin:3px 0;}}
.spl.cond{{border-left-color:var(--accent);}}
.spl.ex{{border-left-width:3px;}}
.spb .atags code{{font-size:10px;padding:2px 7px;}}
.vcw{{display:block;font-size:12.5px;color:var(--ink-dim);line-height:1.4;margin-top:6px;}}
.vgn{{font:600 10px var(--fm);color:var(--accent);margin:9px 0 4px;letter-spacing:.05em;}}
.vclean{{font-size:12px;color:var(--good);padding:4px 0;}}
.vcd .jc{{color:inherit;}}
.vcd.c-g{{background:var(--good-soft);border-color:var(--good);color:var(--good);}}
.vcd.c-b{{background:var(--accent-soft);border-color:var(--accent);color:var(--accent-ink);}}
.vcd.c-o{{background:var(--warn-soft);border-color:var(--warn);color:var(--warn);}}
.vcd.c-q{{background:var(--pending-soft);border-color:var(--pending);color:var(--ink-dim);}}
.vcd.c-r{{background:var(--bad-soft);border-color:var(--bad);color:var(--bad);}}
.vcd .jt{{color:var(--ink);}}
.vcd .jm{{color:inherit;opacity:.9;}}
.vland{{font:600 10.5px var(--fm);color:var(--ink-faint);line-height:1.9;}}
.fwk{{display:grid;grid-template-columns:repeat(auto-fill,minmax(420px,1fr));gap:10px;}}
.fw{{border:1px solid var(--rule);border-left:3px solid var(--good);border-radius:0 8px 8px 0;
 background:var(--surface);padding:11px 13px;}}
.fwq{{font-size:14px;line-height:1.5;font-style:italic;}}
.fwy{{font-size:13px;color:var(--ink-dim);margin-top:6px;line-height:1.45;}}
.fwm{{font:600 10px var(--fm);color:var(--ink-faint);margin-top:7px;letter-spacing:.03em;}}
.prov{{font:600 9.5px var(--fm);color:var(--ink-faint);letter-spacing:.05em;white-space:nowrap;}}
.tabs{{display:none;}}
.vcols{{display:flex;gap:12px;overflow-x:auto;padding-bottom:10px;align-items:flex-start;}}
.vcol{{flex:0 0 400px;border:1px solid var(--rule);border-radius:10px;background:var(--surface);padding:12px 13px;}}
.vch{{border-bottom:1px solid var(--rule);padding-bottom:9px;margin-bottom:9px;}}
.vcn{{display:inline-block;width:22px;height:22px;border-radius:11px;background:var(--accent);color:#fff;
 font:700 12px/22px var(--fm);text-align:center;margin-right:8px;}}
.vch b{{font-size:17px;}}
.vcz{{display:block;font:600 9.5px var(--fm);letter-spacing:.09em;color:var(--ink-faint);margin-top:5px;}}
.vsec{{font:600 9px var(--fm);letter-spacing:.11em;color:var(--ink-faint);margin:12px 0 6px;}}
.vm{{display:flex;gap:8px;padding:5px 0;border-top:1px solid var(--rule);}}
.vm:first-of-type{{border-top:none;}}
.vm.un{{background:var(--bad-soft);border-radius:5px;padding:5px 7px;margin:2px -7px;border-top:none;}}
.vmi{{flex:0 0 14px;font-size:11px;color:var(--ink-dim);}}
.vmt{{font-size:13px;line-height:1.35;}}
.vmo{{display:block;font:600 9.5px var(--fm);color:var(--ink-faint);margin-top:2px;}}
.vm.un .vmo{{color:var(--bad);}}
.vcol .jchips{{display:flex;flex-wrap:wrap;gap:5px;}}
.vcol .achip{{font-size:12.2px;padding:4px 10px;}}
.vcd{{border:1.5px solid;border-radius:7px;padding:7px 9px;margin-bottom:6px;display:flex;gap:8px;}}
.vcd .jt{{font-size:13px;}}
.jhave{{padding-left:39px;margin-bottom:10px;}}
.jhl{{display:block;font:600 9.5px var(--fm);letter-spacing:.11em;color:var(--ink-faint);margin-bottom:6px;}}
.jhl2{{flex:1 1 100%;margin:2px 0 -2px;}}
.jchips{{display:flex;flex-wrap:wrap;gap:6px;}}
.jhave .achip{{font-size:11.5px;padding:4px 10px;}}
.jl{{margin:0 0 4px;padding:14px 0 6px;border-bottom:1px solid var(--rule);}}
.jlh{{display:flex;gap:12px;align-items:flex-start;margin-bottom:10px;}}
.jseq{{flex:0 0 27px;width:27px;height:27px;border-radius:14px;background:var(--accent);color:#fff;
 font:700 14px/27px ui-monospace,monospace;text-align:center;}}
.jseq.own{{background:var(--warn);}}
.jlh b{{display:block;font-size:15px;}}
.jlh span{{display:block;font-size:12px;color:var(--ink-dim);margin-top:2px;}}
.jit{{display:flex;flex-wrap:wrap;gap:8px;padding-left:39px;}}
.jitem{{flex:1 1 430px;min-width:330px;border:1.5px solid;border-radius:8px;padding:9px 11px;display:flex;gap:10px;}}
.jc{{font:700 12px ui-monospace,monospace;flex:0 0 auto;padding-top:1px;}}
.jt{{font-size:13px;line-height:1.35;}}
.jm{{display:block;font:600 10.5px ui-monospace,monospace;margin-top:4px;letter-spacing:.03em;}}
.jnone{{font-size:12.5px;color:var(--ink-faint);font-style:italic;}}
.panel{{display:none;padding-top:20px;}} .panel.active{{display:block;}}
.blurb{{font-size:14px;color:var(--ink-dim);line-height:1.6;max-width:74ch;margin:0 0 16px;}}
.dgwrap{{border:1px solid var(--rule);border-radius:8px;background:var(--surface);padding:10px;overflow-x:auto;}}
svg.dg{{width:100%;min-width:720px;height:auto;display:block;}}
.bnd rect{{fill:none;stroke:var(--ink-faint);stroke-width:1;stroke-dasharray:5 4;opacity:.55;}}
.bnd text{{font-family:var(--fm);font-size:9.5px;fill:var(--ink-faint);letter-spacing:.04em;}}
.bx rect{{fill:var(--surface-2);stroke:var(--pending);stroke-width:1.5;}}
.bx text.t{{font-size:12.5px;font-weight:650;fill:var(--ink);font-family:var(--fd);}}
.bx text.tc{{font-size:9.5px;fill:var(--ink-dim);font-family:var(--fm);}}
.bx text.m{{font-size:9.5px;font-family:var(--fm);font-weight:600;letter-spacing:.04em;text-transform:uppercase;}}
.bx text.n{{font-size:9.5px;fill:var(--ink-dim);font-family:var(--fd);}}
.bx.g rect{{stroke:var(--good);}} .bx.g text.m{{fill:var(--good);}}
.bx.o rect{{stroke:var(--warn);}} .bx.o text.m{{fill:var(--warn);}}
.bx.b rect{{stroke:var(--accent);}} .bx.b text.m{{fill:var(--accent);}}
.bx.q rect{{stroke:var(--pending);}} .bx.q text.m{{fill:var(--pending);}}
.bx.r rect{{stroke:var(--bad);}} .bx.r text.m{{fill:var(--bad);}}
.bx.a rect{{stroke:var(--warn);fill:var(--warn-soft);}} .bx.a text.m{{fill:var(--warn);}}
.bx.d rect{{stroke:var(--bad);stroke-dasharray:5 4;fill:var(--bad-soft);}} .bx.d text.m{{fill:var(--bad);}}
.psn circle,.psn rect{{fill:var(--accent-soft);stroke:var(--accent);stroke-width:1.5;}}
.psn text.t{{font-size:12.5px;font-weight:650;fill:var(--ink);}}
.psn text.tc{{font-size:9.5px;fill:var(--ink-dim);font-family:var(--fm);}}
.ed{{fill:none;stroke:var(--ink-faint);stroke-width:1.4;marker-end:url(#a);}}
.ed.dash{{stroke-dasharray:5 4;}}
marker path{{fill:var(--ink-faint);}}
.el{{font-size:9.5px;fill:var(--ink-faint);font-family:var(--fm);}}
.lg{{display:flex;gap:14px;flex-wrap:wrap;margin-top:12px;font-family:var(--fm);font-size:10px;color:var(--ink-faint);}}
.rels{{display:grid;grid-template-columns:repeat(auto-fill,minmax(300px,1fr));gap:6px;margin-top:14px;}}
.rels div{{font-size:11.5px;line-height:1.45;color:var(--ink-dim);}}
.rels b{{display:block;font-family:var(--fm);font-size:10.5px;color:var(--ink);font-weight:600;}}
.lg i{{display:inline-block;width:9px;height:9px;border-radius:2px;margin-right:5px;vertical-align:middle;}}
.note{{border:1px solid var(--rule);border-left:3px solid var(--bad);border-radius:0 6px 6px 0;background:var(--bad-soft);
padding:12px 14px;font-size:12px;line-height:1.6;margin:18px 0;}}
.note b{{font-weight:650;}} .note ul{{margin:7px 0 0;padding-left:18px;}} .note li{{margin:3px 0;}}
.vwrap{{border:1px solid var(--rule);border-radius:8px;background:var(--surface);overflow:hidden;margin-bottom:22px;}}
.vrow{{display:grid;grid-template-columns:26px 1fr auto;gap:12px;padding:12px 14px;border-top:1px solid var(--rule);align-items:start;}}
.vrow:first-child{{border-top:none;}}
.vn{{font-family:var(--fm);font-size:11.5px;color:var(--ink-faint);font-weight:600;padding-top:2px;}}
.vt{{font-size:13px;font-weight:600;line-height:1.4;overflow-wrap:anywhere;}}
.vd{{font-family:var(--fm);font-size:10.5px;color:var(--ink-faint);margin-top:3px;}}
.vs{{font-family:var(--fm);font-size:9.5px;letter-spacing:.04em;text-transform:uppercase;font-weight:600;padding-top:3px;white-space:nowrap;}}
.cards{{display:grid;grid-template-columns:repeat(auto-fill,minmax(250px,1fr));gap:9px;}}
.card{{border:1px solid var(--rule);border-left:3px solid var(--pending);border-radius:0 5px 5px 0;background:var(--surface);padding:9px 11px;min-width:0;}}
.card .t{{font-size:12.5px;font-weight:600;line-height:1.35;overflow-wrap:anywhere;}}
.card .m{{font-family:var(--fm);font-size:9.5px;letter-spacing:.04em;text-transform:uppercase;margin-top:5px;font-weight:600;}}
.card .w{{font-size:10.5px;color:var(--ink-dim);margin-top:4px;}}
.card.g{{border-left-color:var(--good);}} .card.g .m{{color:var(--good);}}
.card.o{{border-left-color:var(--warn);}} .card.o .m{{color:var(--warn);}}
.card.b{{border-left-color:var(--accent);}} .card.b .m{{color:var(--accent);}}
.card.q{{border-left-color:var(--pending);}} .card.q .m{{color:var(--pending);}}
.card.r{{border-left-color:var(--bad);}} .card.r .m{{color:var(--bad);}}
.lay{{font-family:var(--fm);font-size:9.5px;color:var(--accent);font-weight:600;letter-spacing:.04em;text-transform:uppercase;margin-top:5px;}}\n

.cap{{margin-top:26px}}
.capbar{{display:flex;gap:18px;align-items:center;margin:4px 0 14px}}
.capnum{{font:600 26px var(--fm);font-variant-numeric:tabular-nums;white-space:nowrap}}
.capnum span{{font:400 13px var(--fd);color:var(--ink-dim);margin-left:6px}}
.capun{{font:600 12px var(--fm);color:var(--warn);white-space:nowrap}}
.capband{{border-left:4px solid;padding:4px 0 6px 14px;margin:18px 0 6px}}
.capbt{{font:700 11px var(--fm);letter-spacing:.1em}} .capbt span{{font-weight:500}}
.capbn{{font-size:13px;color:var(--ink-dim);margin:4px 0 8px;max-width:110ch;line-height:1.45}}
.capseq{{font:700 13px var(--fm);color:var(--warn);text-align:right}}
.capg{{font:700 10px var(--fm);letter-spacing:.11em;color:var(--ink-faint);margin:16px 0 6px;
 border-bottom:1px solid var(--rule);padding-bottom:5px}}
.capr{{display:grid;grid-template-columns:20px 22px 34px minmax(240px,1.1fr) minmax(230px,1.2fr) 150px;
 gap:14px;align-items:baseline;padding:6px 0;border-bottom:1px solid var(--rule)}}
.capi{{width:17px;height:17px;border-radius:5px;border:1.5px solid;display:inline-block;
 text-align:center;font-size:11px;line-height:15px;color:var(--good)}}
.capt{{font-size:14px}} .capt em{{display:block;font:600 10px var(--fm);color:var(--accent);font-style:normal;letter-spacing:.05em;margin-top:3px}}.capn2{{font:600 12px var(--fm);color:var(--ink-faint);text-align:right}} .capc{{font-size:13px;color:var(--ink-dim)}}
.capo{{font:600 11.5px var(--fm);text-align:right;letter-spacing:.03em}}
@media (max-width:900px){{.capr{{grid-template-columns:20px 22px 34px 1fr}} .capc,.capo{{grid-column:2}}}}

.sto{{margin-top:28px}}
.sid2{{font:700 9.5px var(--fm);color:#fff;background:#6B3FA0;border-radius:3px;padding:1px 5px;margin-left:6px;letter-spacing:.03em;vertical-align:1px;white-space:nowrap}}
.sid2.no{{background:var(--bad)}}
.covb{{border-left:4px solid #6B3FA0;background:#F3EEF9;border-radius:0 8px 8px 0;padding:11px 15px;font-size:14px;margin:0 0 14px;line-height:1.5}}
.covb.gap{{border-left-color:var(--bad);background:var(--bad-soft)}}
.epc{{margin-top:22px;border:1px solid var(--rule);border-radius:12px;padding:14px 16px;background:var(--surface)}}
.eph{{display:flex;gap:12px;align-items:baseline;flex-wrap:wrap}}
.epid{{font:700 12px var(--fm);color:#fff;background:#6B3FA0;border-radius:5px;padding:3px 9px}}
.eph b{{font-size:17px}} .epn{{font:600 11.5px var(--fm);color:var(--ink-faint);margin-left:auto}}
.epw{{font-size:13px;color:var(--ink-dim);margin:5px 0 12px}}
.stgrid{{display:grid;grid-template-columns:repeat(auto-fill,minmax(500px,1fr));gap:12px}}
.rkstrip{{display:flex;flex-wrap:wrap;gap:8px;align-items:center;margin:4px 0 6px}}
.rkh{{font:700 10.5px var(--fm);letter-spacing:.1em;color:var(--ink-faint);margin-right:4px}}
.rki{{border:1.5px solid;border-radius:16px;padding:5px 12px;font-size:12.8px}}
.rki b{{font-family:var(--fm);margin-right:4px}}
.stc{{border:1px solid var(--rule);border-top:4px solid;border-radius:0 0 10px 10px;padding:11px 13px;background:var(--bg)}}
.sth{{display:flex;gap:9px;align-items:center}}
.rk{{font:700 15px var(--fm);color:#fff;background:var(--warn);border-radius:13px;width:26px;height:26px;
 display:inline-flex;align-items:center;justify-content:center}}
.rk.nr{{background:var(--rule);color:var(--ink-faint)}}
.sid{{font:700 12px var(--fm);color:var(--ink-faint)}}
.sst{{font:700 10px var(--fm);letter-spacing:.06em;border-radius:4px;padding:3px 8px;margin-left:auto}}
.stt{{font-size:15px;font-weight:600;margin:8px 0 4px;line-height:1.3}}
.sta{{font-size:13px;color:var(--ink-dim);font-style:italic;line-height:1.45}}
.stm{{font:600 11px var(--fm);color:var(--accent-ink);margin:8px 0 6px}}
.stm span{{color:var(--ink-faint);letter-spacing:.08em;margin-right:4px}}
.tkr{{display:grid;grid-template-columns:42px 1fr 104px;gap:10px;align-items:start;
 padding:6px 0;border-top:1px solid var(--rule);font-size:12.8px}}
.tkt{{font:700 9.5px var(--fm);color:#fff;background:var(--accent);border-radius:3px;padding:2px 0;text-align:center}}
.tkr.bug .tkt{{background:var(--bad)}}
.tkx{{line-height:1.4}} .tkc{{font:700 11.5px var(--fm);color:var(--accent-ink);margin-right:4px}}
.tkr.bug .tkc{{color:var(--bad);font-weight:600;font-size:10.5px}}
.tkp{{display:block;font:600 10.5px var(--fm);color:var(--ink-faint);margin-top:2px}}
.tks{{font:700 9.5px var(--fm);border-radius:4px;padding:2px 6px;text-align:center}}
.hand{{font-weight:500;opacity:.7;letter-spacing:.04em}}
.stn{{font-size:12.3px;color:var(--ink-dim);border-left:3px solid var(--warn);padding:5px 9px;margin-top:8px;line-height:1.45}}
.uns{{margin-top:22px}}
.stg,.fp{{margin-top:26px}}
.stgrow{{display:grid;grid-template-columns:repeat(auto-fit,minmax(176px,1fr));gap:12px;margin-top:10px}}
.stgi{{border-top:3px solid var(--pending);padding-top:9px;position:relative}}
.stgi.g{{border-top-color:var(--good)}} .stgi.o{{border-top-color:var(--warn)}}
.stgi.now{{background:var(--warn-soft);border-radius:0 0 8px 8px;padding:9px 10px 10px;margin-top:-0px}}
.stghere{{font:700 9px var(--fm);letter-spacing:.14em;color:var(--warn);margin-bottom:5px}}
.stgn{{font-size:13.5px;line-height:1.3}} .stgn b{{font-family:var(--fm);color:var(--accent);margin-right:5px}}
.stgn em{{font:600 9px var(--fm);color:var(--good);font-style:normal;letter-spacing:.06em;display:block;margin-top:3px}}
.stgg{{font-size:11.5px;color:var(--ink-dim);line-height:1.4;margin-top:4px}}
.fprow{{display:grid;grid-template-columns:repeat(auto-fit,minmax(300px,1fr));gap:10px;margin-top:10px}}
.fpi{{display:flex;gap:11px;border:1px solid var(--rule);border-left:4px solid var(--pending);
 border-radius:0 9px 9px 0;background:var(--surface);padding:11px 13px}}
.fpi.g{{border-left-color:var(--good)}} .fpi.b{{border-left-color:var(--accent)}}
.fpi.o{{border-left-color:var(--warn)}} .fpi.r{{border-left-color:var(--bad);background:var(--bad-soft)}}
.fpn{{font:700 21px var(--fm);color:var(--ink-faint);flex:0 0 26px;line-height:1}}
.fpc{{font:700 13px var(--fm);color:var(--accent-ink)}}
.fpc span{{font-weight:500;color:var(--ink-faint);margin-left:8px;letter-spacing:.04em}}
.fpt{{font-size:14px;font-weight:600;margin-top:4px;line-height:1.3}}
.fpw{{font-size:12.5px;color:var(--ink-dim);margin-top:5px;line-height:1.45}}
.fpm{{font:600 10px var(--fm);color:var(--ink-faint);margin-top:7px;letter-spacing:.04em}}
.fpend{{margin-top:12px;font-size:14.5px;font-weight:600;border-left:4px solid var(--accent);
 background:var(--accent-soft);border-radius:0 8px 8px 0;padding:12px 15px;line-height:1.5}}
.ms{{margin-top:22px;}}\n.ms-h{{font-family:var(--fm);font-size:10px;letter-spacing:.07em;text-transform:uppercase;color:var(--ink-faint);font-weight:600;margin-bottom:10px;}}\n.ms-track{{display:grid;grid-template-columns:repeat(auto-fit,minmax(230px,1fr));gap:14px;align-items:start;}}\n.ms-i{{border-top:2px solid var(--pending);padding-top:8px;}}\n.ms-i.g{{border-top-color:var(--good);}} .ms-i.o{{border-top-color:var(--warn);}}\n.ms-i.b{{border-top-color:var(--accent);}} .ms-i.q{{border-top-color:var(--rule);}}\n.ms-n{{font-size:14px;font-weight:650;line-height:1.3;}}\n.ms-b{{height:4px;border-radius:2px;background:var(--pending-soft);margin:7px 0 5px;overflow:hidden;}}\n.ms-b i{{display:block;height:100%;background:currentColor;}}\n.ms-i.g .ms-b i{{background:var(--good);}} .ms-i.o .ms-b i{{background:var(--warn);}}\n.ms-i.b .ms-b i{{background:var(--accent);}} .ms-i.q .ms-b i{{background:var(--pending);}}\n.ms-c{{font-family:var(--fm);font-size:9.5px;color:var(--ink-faint);}}\n.ms-s{{margin-top:8px;border-top:1px solid var(--rule);padding-top:7px;}}\n.ms-r{{font-size:10.5px;line-height:1.4;color:var(--ink-dim);padding:3px 0 3px 7px;border-left:2px solid var(--pending);margin-bottom:3px;}}\n.ms-r b{{font-family:var(--fm);font-size:10px;color:var(--ink);margin-right:5px;}}\n.ms-r span{{display:block;font-family:var(--fm);font-size:9px;text-transform:uppercase;letter-spacing:.04em;opacity:.85;}}\n.ms-r.g{{border-left-color:var(--good);}} .ms-r.g span{{color:var(--good);}}\n.ms-r.o{{border-left-color:var(--warn);}} .ms-r.o span{{color:var(--warn);}}\n.ms-r.b{{border-left-color:var(--accent);}} .ms-r.b span{{color:var(--accent);}}\n.ms-r.q{{border-left-color:var(--pending);}} .ms-r.q span{{color:var(--pending);}}\n.ms-r.r{{border-left-color:var(--bad);}} .ms-r.r span{{color:var(--bad);}}\n.ms-r.d{{border-left-style:dashed;border-left-color:var(--bad);}} .ms-r.d span{{color:var(--bad);}}\n.ms-m{{font-size:12.5px;color:var(--ink-dim);line-height:1.45;margin-top:4px;}}\n.dseq{{border:1px solid var(--rule);border-radius:8px;background:var(--surface);overflow:hidden;margin-bottom:24px;}}\n.drow{{display:grid;grid-template-columns:24px 54px 1fr 92px 96px;gap:10px;padding:10px 14px;border-top:1px solid var(--rule);align-items:baseline;border-left:3px solid var(--pending);}}\n.drow:first-child{{border-top:none;}}\n.dn,.dnum{{font-family:var(--fm);font-size:10.5px;color:var(--ink-faint);}}\n.dnum{{font-weight:600;color:var(--ink);}}\n.dwhat{{font-size:12.5px;line-height:1.4;}}\n.dlayer{{font-family:var(--fm);font-size:9.5px;color:var(--ink-dim);text-transform:uppercase;letter-spacing:.04em;}}\n.dst{{font-family:var(--fm);font-size:9.5px;font-weight:600;text-transform:uppercase;letter-spacing:.04em;text-align:right;}}\n.drow.g{{border-left-color:var(--good);}} .drow.g .dst{{color:var(--good);}}\n.drow.o{{border-left-color:var(--warn);}} .drow.o .dst{{color:var(--warn);}}\n.drow.b{{border-left-color:var(--accent);}} .drow.b .dst{{color:var(--accent);}}\n.drow.q{{border-left-color:var(--pending);}} .drow.q .dst{{color:var(--pending);}}\n.drow.a{{border-left-color:var(--warn);background:var(--warn-soft);}} .drow.a .dst{{color:var(--warn);}}\n.drow.here{{background:var(--accent-soft);}}\n.drow.here .dst{{color:var(--accent-ink);}}\n.drow.here .dwhat{{font-weight:650;}}\n.drow.d{{border-left-style:dashed;border-left-color:var(--bad);}} .drow.d .dst{{color:var(--bad);}}\n@media (max-width:640px){{.drow{{grid-template-columns:22px 50px 1fr;}} .dlayer,.dst{{grid-column:3;text-align:left;}}}}\n.sec{{font-size:13px;font-weight:650;margin:26px 0 10px;}}\n.epic{{border:1px solid var(--rule);border-radius:8px;background:var(--surface);padding:14px 16px;margin-bottom:14px;}}\n.epic-h{{display:flex;justify-content:space-between;align-items:baseline;gap:10px;flex-wrap:wrap;}}\n.epic-n{{font-family:var(--fm);font-size:12.5px;font-weight:600;letter-spacing:.04em;}}\n.epic-g{{font-size:12px;color:var(--ink-dim);line-height:1.55;margin:8px 0 4px;max-width:78ch;}}\n.col{{margin-top:14px;}}\n.col-h{{font-family:var(--fm);font-size:10px;letter-spacing:.06em;text-transform:uppercase;font-weight:600;margin-bottom:7px;}}\n.card.d{{border-left-style:dashed;border-left-color:var(--bad);}} .card.d .m{{color:var(--bad);}}\n.note{{border-left-color:var(--warn);background:var(--warn-soft);}}\n.band{{margin-top:22px;}}
.band-h{{font-size:12.5px;font-weight:650;margin-bottom:9px;display:flex;gap:9px;align-items:baseline;flex-wrap:wrap;}}
.band-h span.c{{font-family:var(--fm);font-size:10px;color:var(--ink-faint);font-weight:400;}}
.pill{{font-family:var(--fm);font-size:10px;padding:3px 8px;border-radius:12px;font-weight:500;white-space:nowrap;}}
.pill.g{{background:var(--good-soft);color:var(--good);}} .pill.o{{background:var(--warn-soft);color:var(--warn);}}
.pill.b{{background:var(--accent-soft);color:var(--accent-ink);}} .pill.q{{background:var(--pending-soft);color:var(--pending);}}
.pill.r{{background:var(--bad-soft);color:var(--bad);}}
footer{{margin-top:38px;padding-top:14px;border-top:1px solid var(--rule);font-size:10.5px;color:var(--ink-faint);font-family:var(--fm);line-height:1.7;}}
@media (max-width:640px){{.cards{{grid-template-columns:1fr;}} .vrow{{grid-template-columns:24px 1fr;}} .vs{{grid-column:2;padding-top:5px;}}}}

.alvl{{border:1px solid var(--line);border-radius:10px;padding:14px 16px;margin:12px 0;background:var(--card)}}
.ahd{{display:flex;align-items:baseline;gap:12px;margin-bottom:10px}}
.ahd b{{font-size:13px;letter-spacing:.06em}}
.ahd span{{font-size:12px;color:var(--muted)}}
.achips{{display:flex;flex-wrap:wrap;gap:8px}}
.achip{{display:inline-flex;align-items:center;gap:8px;border:1px solid;border-radius:16px;padding:5px 12px;font-size:12.5px;line-height:1.3}}
.achip i{{width:8px;height:8px;border-radius:50%;flex:0 0 8px}}
.alist{{margin:10px 0 18px;padding-left:20px}}
.alist li{{margin:8px 0;font-size:14.5px;line-height:1.5}}

.nx{{border:1px solid var(--accent);border-left:4px solid var(--accent);border-radius:0 10px 10px 0;
background:var(--accent-soft);padding:16px 20px;margin:20px 0 10px;}}
.nx-k{{font-family:var(--fm);font-size:10px;letter-spacing:.13em;color:var(--accent-ink);font-weight:600;}}
.nx-t{{font-size:17px;line-height:1.35;margin:8px 0 14px;color:var(--ink);}}
.nx-t b{{font-family:var(--fm);font-weight:600;}}
.nx-g{{display:grid;grid-template-columns:repeat(auto-fit,minmax(240px,1fr));gap:12px;}}
.nx-g div{{font-size:12.5px;line-height:1.5;color:var(--ink);}}
.nx-g span{{display:block;font-family:var(--fm);font-size:9.5px;letter-spacing:.07em;color:var(--accent-ink);
font-weight:600;margin-bottom:3px;}}
.orient{{font-size:12px;line-height:1.7;color:var(--ink-dim);margin:0 0 6px;}}
.orient b{{color:var(--ink);font-weight:600;}}

.kb{{margin-top:6px}}
.kh{{display:grid;grid-template-columns:repeat(4,1fr);gap:10px;position:sticky;top:0;background:var(--bg);
padding:6px 0 8px;font-family:var(--fm);font-size:10px;letter-spacing:.1em;text-transform:uppercase;
color:var(--ink-faint);font-weight:600;border-bottom:1px solid var(--rule);z-index:2}}
.klane{{margin-top:18px}}
.kl-h{{display:flex;gap:12px;align-items:baseline;flex-wrap:wrap;margin-bottom:8px}}
.kl-h b{{font-size:13.5px}}
.kl-h span{{font-size:11.5px;color:var(--ink-faint)}}
.kgrid{{display:grid;grid-template-columns:repeat(4,1fr);gap:10px;align-items:start}}
.kcol{{background:var(--surface-2);border-radius:8px;padding:8px;min-height:56px;display:flex;
flex-direction:column;gap:8px}}
.kc{{background:var(--surface);border:1px solid var(--rule);border-left:3px solid var(--pending);
border-radius:0 6px 6px 0;padding:8px 10px}}
.kn{{font-family:var(--fm);font-size:11px;font-weight:600;color:var(--ink-dim)}}
.kt{{font-size:12.5px;line-height:1.35;margin-top:3px;overflow-wrap:anywhere}}
.kd{{font-family:var(--fm);font-size:9.5px;color:var(--ink-faint);margin-top:5px}}
.kp{{font-family:var(--fm);font-size:9.5px;color:var(--bad);margin-top:5px}}
.kc.g{{border-left-color:var(--good)}} .kc.o{{border-left-color:var(--warn)}}
.kc.b{{border-left-color:var(--accent)}} .kc.q{{border-left-color:var(--pending)}}
.kc.r{{border-left-color:var(--bad)}}
.kc.d{{border-left-color:var(--bad);border-left-style:dashed}}
@media (max-width:820px){{.kh{{display:none}} .kgrid{{grid-template-columns:1fr}}}}

.kswitch{{display:flex;gap:6px;margin:6px 0 14px}}
.ksw{{font-family:var(--fm);font-size:11.5px;padding:7px 14px;border:1px solid var(--rule);
background:var(--surface);color:var(--ink-dim);border-radius:16px;cursor:pointer}}
.ksw.on{{background:var(--accent-soft);border-color:var(--accent);color:var(--accent-ink);font-weight:600}}
.kn i{{font-style:normal;font-family:var(--fd);font-size:9.5px;color:var(--accent);
margin-left:8px;letter-spacing:.03em}}
.kh{{display:grid;grid-template-columns:repeat(4,1fr);gap:10px;padding:0 0 6px;
font-family:var(--fm);font-size:9.5px;letter-spacing:.1em;text-transform:uppercase;
color:var(--ink-faint);font-weight:600;border-bottom:1px solid var(--rule);margin-bottom:8px}}

.alv{{border:1px solid var(--rule);border-radius:10px;padding:18px 20px;margin:14px 0;background:var(--surface)}}
.alv.l2{{background:var(--surface-2)}}
.alv-h{{display:flex;justify-content:space-between;align-items:baseline;gap:12px;flex-wrap:wrap}}
.alv-h b{{font-size:18px}}
.role{{font-family:var(--fm);font-size:10.5px;color:var(--accent);margin-left:10px;
border:1px solid var(--rule);border-radius:12px;padding:3px 9px}}
.alv-s{{font-size:13px;color:var(--ink-dim);line-height:1.55;margin:8px 0 12px;max-width:92ch}}
.al{{list-style:none;margin:6px 0 0;padding:0}}
.al li{{display:flex;gap:9px;align-items:flex-start;font-size:13px;line-height:1.5;margin:5px 0}}
.al li i{{width:8px;height:8px;border-radius:50%;flex:0 0 8px;margin-top:6px}}
.al.plain li{{padding-left:14px;position:relative}}
.al.plain li:before{{content:"—";position:absolute;left:0;color:var(--ink-faint)}}
.al li b{{font-family:var(--fm);font-size:10px;color:var(--accent);white-space:nowrap;
border:1px solid var(--rule);border-radius:10px;padding:2px 7px;margin-left:auto}}
.asp{{border:1px solid var(--rule);border-radius:8px;background:var(--bg);padding:12px 14px;margin:14px 0}}
.asp-h{{font-size:12.5px;font-weight:600;margin-bottom:8px}}
.asp-g{{display:grid;grid-template-columns:repeat(auto-fill,minmax(300px,1fr));gap:4px 16px}}
.asp-g div{{display:flex;gap:10px;font-size:12px;line-height:1.5}}
.asp-g code{{font-family:var(--fm);font-size:11.5px;color:var(--ink);flex:0 0 150px}}
.asp-g span{{color:var(--ink-dim)}}
.acol2{{display:grid;grid-template-columns:1fr 1fr;gap:22px;margin-top:14px}}
.acol3{{display:grid;grid-template-columns:1fr 1fr 1fr;gap:20px;margin-top:10px}}
.acol2 h5,.acol3 h5{{font-family:var(--fm);font-size:10px;letter-spacing:.09em;text-transform:uppercase;
color:var(--ink-faint);margin:0 0 4px;font-weight:600}}
.aflow{{text-align:center;font-family:var(--fm);font-size:11px;color:var(--ink-faint);padding:4px 0}}
.and{{border:1px solid var(--rule);border-left:3px solid var(--pending);border-radius:0 8px 8px 0;
background:var(--surface);padding:14px 16px;margin:10px 0}}
.and.isagent{{border-left-color:var(--warn);background:var(--warn-soft)}}
.and-h{{display:flex;align-items:baseline;gap:12px;flex-wrap:wrap}}
.and-h b{{font-size:15.5px}}
.agent{{font-family:var(--fm);font-size:10px;font-weight:600;color:var(--warn);
border:1px solid var(--warn);border-radius:10px;padding:2px 8px}}
.notagent{{font-family:var(--fm);font-size:10px;color:var(--ink-faint)}}
.ac{{font-family:var(--fm);font-size:10px;border:1px solid;border-radius:10px;padding:2px 8px;margin-left:auto}}
.and-o{{font-size:13.5px;margin:8px 0 2px;color:var(--ink)}}
.agrid{{display:grid;grid-template-columns:repeat(auto-fill,minmax(270px,1fr));gap:10px}}
.amw{{border:1px solid var(--rule);border-left:3px solid var(--pending);border-radius:0 6px 6px 0;
background:var(--surface);padding:10px 12px}}
.amw-h{{font-size:13px;font-weight:600;display:flex;gap:8px;align-items:baseline}}
.amw-h em{{font-family:var(--fm);font-style:normal;font-size:11px;color:var(--ink-faint)}}
.amw p{{font-size:12px;color:var(--ink-dim);line-height:1.5;margin:5px 0 0}}
.amw b{{display:inline-block;font-family:var(--fm);font-size:10px;color:var(--accent);margin-top:6px;
border:1px solid var(--rule);border-radius:10px;padding:2px 7px}}
.atbl{{border:1px solid var(--rule);border-radius:8px;overflow:hidden;background:var(--surface)}}
.atr{{display:grid;grid-template-columns:70px 1fr 140px 1.4fr 130px;gap:12px;padding:10px 14px;
border-top:1px solid var(--rule);font-size:12.5px;line-height:1.45;align-items:baseline}}
.atbl.wide .atr{{grid-template-columns:150px 1.4fr 1.4fr 130px}}
.atr:first-child{{border-top:none}}
.atr.head{{font-family:var(--fm);font-size:9.5px;letter-spacing:.08em;text-transform:uppercase;
color:var(--ink-faint);font-weight:600;background:var(--surface-2)}}
.atr .dim{{color:var(--ink-dim)}}
.atr code{{font-family:var(--fm);font-size:11.5px}}
.atags{{display:flex;flex-wrap:wrap;gap:6px;margin-top:6px}}
.atags code{{font-family:var(--fm);font-size:11.5px;background:var(--good-soft);color:var(--good);
border-radius:10px;padding:3px 9px}}
@media (max-width:900px){{.acol2,.acol3{{grid-template-columns:1fr}}
.atr,.atbl.wide .atr{{grid-template-columns:1fr}} .atr.head{{display:none}}}}

.ddiag{{border:1px solid var(--rule);border-radius:10px;overflow:hidden;background:#FFFFFF;margin:6px 0 4px}}
.dsvg{{width:100%;height:auto;display:block;min-width:1100px}}
.ddiag{{overflow-x:auto}}
.dh1{{font-size:20px;font-weight:600;fill:#16150F;font-family:var(--fd)}}
.dh2{{font-size:16px;font-weight:600;fill:#16150F;font-family:var(--fd)}}
.dagent{{font-size:16px;font-weight:700;font-family:var(--fd)}}
.dsub{{font-size:13px;fill:#5B5648;font-family:var(--fd)}}
.dsub2{{font-size:13px;fill:#3F6A5C;font-family:var(--fd)}}
.dedge{{font-size:12.5px;fill:#6A6558;font-family:var(--fd)}}
.dpill{{font-size:11px;font-weight:600;font-family:var(--fm)}}
.dtool{{font-size:11.5px;font-family:var(--fm)}}
.dfoot{{font-size:12.5px;fill:#5B5648;font-family:var(--fd)}}
</style>
<div class="wrap">
<div class="eyebrow">AGENT IMPROVE — DMAIC REFACTOR</div>
<h1>Control Board</h1>
<div class="built">BUILT FROM <b>{e(sha)}</b> &middot; {e(subject[:90])} &middot; {now}<br>
The pre-commit hook builds this page on top of the commit before the one being made. <b>If {e(sha)} is not the
parent of the newest commit in git log, the last build FAILED and this page is stale</b>; the hook printed a
warning when it did.</div>
<div class="prov">GENERATED — no status on this page is typed by hand except where labelled HAND or RELAYED.<br>
Source: <b>agent-improve/docs/board.html</b>, read from the working tree and parsed. That file is itself generated by
<b>.claude/hooks/build_board.py</b> on every commit from Appendix D, ARCHITECTURE.md's markers and git log.<br>
Refreshed <b>{now}</b> · last spine step landed <b>{e(str(d["last_step"]))}</b> · drawings follow C4 level 2
(a container is an application or a data store).<br>\nThe repo board is regenerated by a pre-commit hook, so it <b>lags one commit</b> (ARCHITECTURE.md v1.57). A step committed moments ago can still read as ready here.</div>
<div class="sum"><div class="big">{d["landed"]} / {d["total"]}</div><div class="s">spine steps landed · {d["pct"]}%</div>
<div class="s">{d["markers_open"]} of {d["markers_total"]} architecture markers still open</div></div>
<div class="bar"><i style="width:{d["pct"]}%"></i></div>{NEXT_HTML}{INTEGRITY_HTML}{BANDS_HTML}
<div class="tabs" role="tablist">''')
    for i,(k,lab) in enumerate(TABS):
        a(f'<button class="tab" role="tab" data-tab="{k}" aria-selected="{"true" if i==0 else "false"}">{e(lab)}</button>')
    a('</div>')

    legend = ('<div class="lg">'
      '<span><i style="background:var(--good)"></i>built</span>'
      '<span><i style="background:var(--warn)"></i>building now / disputed</span>'
      '<span><i style="background:var(--accent)"></i>ready</span>'
      '<span><i style="background:var(--pending)"></i>queued</span>'
      '<span><i style="background:var(--bad)"></i>blocked</span>'
      '<span><i style="background:var(--bad-soft);border:1px dashed var(--bad)"></i>unmeasured — no step owns it</span>'
      '</div>')

    for i,(k,lab) in enumerate(TABS):
        a(f'<div class="panel{" active" if i==0 else ""}" id="panel-{k}">')
        a(system_html(d))
        a('</div>')

    a('''<footer>Regenerated by the pre-commit hook on every commit, after build_board.py, into agent-improve/docs/control-board.html.
The plan lives in stories.py. Steps, markers and stages are parsed from docs/board.html; rows proven and story status from Appendix H; task status and NEXT from git log and the rank. Nothing on this page is a status typed by hand except where marked HAND or RELAYED.</footer></div>
<script>
(function(){var t=document.querySelectorAll('.tab'),p=document.querySelectorAll('.panel');
t.forEach(function(b){b.addEventListener('click',function(){
t.forEach(function(x){x.setAttribute('aria-selected',x.dataset.tab===b.dataset.tab?'true':'false');});
p.forEach(function(x){x.classList.remove('active');});
var el=document.getElementById('panel-'+b.dataset.tab); if(el)el.classList.add('active');});});var sw=document.querySelectorAll('.ksw');sw.forEach(function(b){b.addEventListener('click',function(){sw.forEach(function(x){x.classList.toggle('on',x===b);});document.getElementById('grp-stage').style.display=b.dataset.g==='stage'?'':'none';document.getElementById('grp-area').style.display=b.dataset.g==='area'?'':'none';});});})();
</script>''')
    pathlib.Path(out_path).write_text('\n'.join(P), encoding='utf-8')
    print(f'wrote {out_path} · {d["landed"]}/{d["total"]} · {len(findings)} unmeasured boxes')

if __name__ == '__main__':
    try:
        build(sys.argv[1], sys.argv[2])
    except Exception as exc:                        # noqa: BLE001
        # Fail OPEN for the commit, never silently: the previous page stays, and
        # its BUILT FROM line now names an older commit than the parent.
        print('  [control-board] WARNING: NOT regenerated — %r. %s still shows the '
              'previous build; its BUILT FROM line is now stale.' % (exc, sys.argv[2]), file=sys.stderr)
        sys.exit(1)
