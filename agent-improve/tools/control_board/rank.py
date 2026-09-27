"""The order of work, computed — ADR-0058 (ACCEPTED, founder 2026-09-27), brief Part F3.

The rank of every failing feature is computed on every commit from recorded inputs;
it is never stored. Inputs: the requirement's MoSCoW (business.md / platform.md),
the feature's `belt_impact`, `rework_risk`, `effort`, `depends_on` and
`priority_override` (docs/define_features.json), and the test record.

    tier 1   belt impact dead_end / wrong_data / data_loss AND the requirement is Must
    tier 2   Must · tier 3 Should · tier 4 Could · Won't-now is not ranked
    score    (impact + rework risk + unblocks) ÷ effort, within a tier
    a feature never ranks above a failing feature it depends on: a dependency takes the
    best tier of the failing features that depend on it, and is ordered before them
    a founder override (`priority_override: {rank_tier, reason}`) sets the tier and wins

A MoSCoW of `?` (not yet ratified) ranks as Must, and its reason says "provisional"
(founder answer, 2026-09-27). The scales are tunable only by a founder ruling.

    python tools/control_board/rank.py            # the ranked queue per lane, with reasons
    python tools/control_board/rank.py --check    # the feature fields are valid (pre-commit)
"""
from __future__ import annotations

import sys
from pathlib import Path

_HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(_HERE))

import features as F  # noqa: E402

#: The scales (brief Part F3.3) — tunable only by a founder ruling.
IMPACT = {"dead_end": 3, "wrong_data": 3, "data_loss": 3, "degraded": 1, "none": 0}
BELT_BLOCKING = frozenset({"dead_end", "wrong_data", "data_loss"})
REWORK = {"high": 2, "low": 0}
EFFORT = {"S": 1, "M": 2, "L": 3}
MOSCOW_TIER = {"Must": 2, "?": 2, "Should": 3, "Could": 4}
#: Milestones M1–M3 are tiers 1–3 (founder ruling 1 on the Parts A–D report, 2026-09-27).
MILESTONES = {"M1": 1, "M2": 2, "M3": 3}
#: Where a feature sits on the board's value stream (brief Part F7).
PHASES = ("define", "measure", "analyse", "improve", "control")
STAGES = ("open_case", "coached", "report", "approve", "record_written", "next_phase")
LAYERS = ("screen", "api", "coaching", "gate", "persistence", "platform")


def problems(features: list[dict]) -> list[str]:
    """Every feature carries valid F3 fields."""
    out = []
    for f in features:
        fid = f["id"]
        if f.get("belt_impact") not in IMPACT:
            out.append(f"{fid}: belt_impact {f.get('belt_impact')!r} is not one of {sorted(IMPACT)}")
        if f.get("rework_risk") not in REWORK:
            out.append(f"{fid}: rework_risk {f.get('rework_risk')!r} is not high or low")
        if f.get("effort") not in EFFORT:
            out.append(f"{fid}: effort {f.get('effort')!r} is not S, M or L")
        for key, allowed in (("phase", PHASES), ("stage", STAGES), ("layer", LAYERS)):
            if f.get(key) not in allowed:
                out.append(f"{fid}: {key} {f.get(key)!r} is not one of {list(allowed)}")
        o = f.get("priority_override", "missing")
        if o == "missing":
            out.append(f"{fid}: no priority_override field (null, or {{rank_tier, reason}})")
        elif o is not None and not (isinstance(o, dict) and o.get("rank_tier") in (1, 2, 3, 4)
                                    and str(o.get("reason") or "").strip()):
            out.append(f"{fid}: priority_override must be null or {{rank_tier: 1-4, reason}}")
    return out


def _dependents(features: list[dict], failing: set[str]) -> dict[str, set[str]]:
    """For each feature, the failing features that depend on it, transitively."""
    direct: dict[str, set[str]] = {f["id"]: set() for f in features}
    for f in features:
        for d in f["depends_on"]:
            if d in direct:
                direct[d].add(f["id"])
    out: dict[str, set[str]] = {}
    for fid in direct:
        seen: set[str] = set()
        stack = list(direct[fid])
        while stack:
            x = stack.pop()
            if x not in seen:
                seen.add(x)
                stack.extend(direct[x])
        out[fid] = seen & failing
    return out


def rank(features: list[dict] | None = None, res: dict | None = None,
         reqs: dict[str, dict] | None = None) -> list[dict]:
    """The failing, ranked features, best first: {id, lane, rank, tier, score, reason}."""
    features = F.load() if features is None else features
    res = F.results() if res is None else res
    reqs = F.requirements() if reqs is None else reqs
    st = F.status(features, res)
    failing = {i for i, s in st.items() if s == "failing"}
    by_id = {f["id"]: f for f in features}
    dependents = _dependents(features, failing)

    own: dict[str, int | None] = {}
    why: dict[str, list[str]] = {}
    score: dict[str, float] = {}
    for fid in sorted(failing):
        f = by_id[fid]
        moscow = (reqs.get(f.get("requirement", "")) or {}).get("moscow") or "?"
        impact = f.get("belt_impact", "none")
        prov = " (provisional — MoSCoW ?)" if moscow == "?" else ""
        if moscow == "Won't-now":
            own[fid], why[fid] = None, [f"not ranked: {f.get('requirement')} is Won't-now"]
        elif impact in BELT_BLOCKING and MOSCOW_TIER.get(moscow) == 2:
            own[fid], why[fid] = 1, [f"tier 1: {impact} and {f.get('requirement')} is Must{prov}"]
        else:
            own[fid] = MOSCOW_TIER.get(moscow, 2)
            why[fid] = [f"tier {own[fid]}: {f.get('requirement')} is {'Must' if moscow == '?' else moscow}{prov}"]
        n = len(dependents[fid])
        e = f.get("effort", "M")
        rework = REWORK.get(str(f.get("rework_risk", "low")), 0)
        score[fid] = (IMPACT.get(impact, 0) + rework + n) / EFFORT.get(e, 2)
        why[fid].append(f"score {score[fid]:.2f} = ({IMPACT.get(impact, 0)} {impact} + "
                        f"{rework} rework + {n} unblocked) ÷ {EFFORT.get(e, 2)} ({e})")
        o = f.get("priority_override")
        if o:
            own[fid] = o["rank_tier"]
            why[fid].insert(0, f"founder override to tier {o['rank_tier']}: {o['reason']}")

    # A dependency takes the best tier of the failing features that depend on it.
    tier = dict(own)
    for fid in failing:
        if by_id[fid].get("priority_override"):
            continue
        pulls = [(tier_of, d) for d in dependents[fid] if (tier_of := own.get(d)) is not None]
        if pulls:
            best, who = min(pulls)
            if tier[fid] is None or best < tier[fid]:  # type: ignore[operator]
                tier[fid] = best
                why[fid].insert(0, f"raised to tier {best}: {who} depends on it")

    ranked = sorted((i for i in failing if tier[i] is not None),
                    key=lambda i: (tier[i], -score[i], i))
    # Never above a failing dependency: take the best-sorted feature whose deps are placed.
    placed: list[str] = []
    pending = list(ranked)
    while pending:
        for k, fid in enumerate(pending):
            deps = [d for d in F.blockers(fid, features, st) if d in pending and d != fid]
            if not deps:
                placed.append(pending.pop(k))
                break
        else:                                      # a cycle: keep the sorted order
            placed.extend(pending)
            break
    return [{"id": fid, "lane": by_id[fid]["lane"], "rank": n + 1, "tier": tier[fid],
             "score": round(score[fid], 2), "reason": " · ".join(why[fid])}
            for n, fid in enumerate(placed)]


def tiers(features: list[dict] | None = None, reqs: dict[str, dict] | None = None) -> dict[str, int | None]:
    """Every feature's tier as if nothing passed — what a milestone counts (M1–M3 = tiers 1–3)."""
    features = F.load() if features is None else features
    ranked = rank(features, {"outcomes": {}}, reqs)
    got = {r["id"]: r["tier"] for r in ranked}
    return {f["id"]: got.get(f["id"]) for f in features}


def milestones(features: list[dict] | None = None, res: dict | None = None,
               reqs: dict[str, dict] | None = None) -> dict[str, dict]:
    """{M1: {tier, passing, total}, …} — passing features of the milestone's tier ÷ all of them."""
    features = F.load() if features is None else features
    res = F.results() if res is None else res
    st = F.status(features, res)
    t = tiers(features, reqs)
    return {m: {"tier": n, "total": sum(1 for v in t.values() if v == n),
                "passing": sum(1 for i, v in t.items() if v == n and st[i] == "passing")}
            for m, n in MILESTONES.items()}


def next_per_lane(ranked: list[dict]) -> dict[str, str | None]:
    """Each lane takes its top-ranked failing feature."""
    out: dict[str, str | None] = {lane: None for lane in F.LANES}
    for r in ranked:
        if out.get(r["lane"]) is None:
            out[r["lane"]] = r["id"]
    return out


#: A work package's size (brief Part F9.2): effort points, S = 1, M = 2, L = 3.
PACKAGE_POINTS = 5


def _modules(f: dict) -> set[str]:
    return {c.split("::", 1)[0] for c in ((f.get("sources") or {}).get("code") or [])
            if "/tests/" not in c}


def _same_area(f: dict, g: dict) -> bool:
    """Same layer AND stage (both set), or a shared product module in their sources."""
    if f.get("layer") and f.get("stage") and (f["layer"], f["stage"]) == (g.get("layer"), g.get("stage")):
        return True
    return bool(_modules(f) & _modules(g))


def packages(features: list[dict] | None = None, ranked: list[dict] | None = None,
             res: dict | None = None) -> dict[str, dict]:
    """Each lane's next work package (brief Part F9.2): its top-ranked failing feature, then the
    next-ranked features of the lane, in rank order, that share its area (same layer and stage,
    or the same module) or depend on a feature already in the package — until 5 effort points.
    A feature of another area is never pulled ahead of its rank: it ends the package (and
    starts the next one); so does one that would push the package past 5 points."""
    features = F.load() if features is None else features
    ranked = rank(features, res) if ranked is None else ranked
    by_id = {f["id"]: f for f in features}
    out: dict[str, dict] = {}
    for lane in F.LANES:
        queue = [r["id"] for r in ranked if r["lane"] == lane]
        if not queue:
            out[lane] = {"features": [], "points": 0}
            continue
        pkg = [queue[0]]
        points = EFFORT.get(by_id[queue[0]].get("effort", "M"), 2)
        for fid in queue[1:]:
            f = by_id[fid]
            e = EFFORT.get(f.get("effort", "M"), 2)
            related = any(_same_area(by_id[p], f) for p in pkg) or bool(set(f["depends_on"]) & set(pkg))
            if not related or points + e > PACKAGE_POINTS:
                break
            pkg.append(fid)
            points += e
        out[lane] = {"features": pkg, "points": points}
    return out


def main(argv: list[str]) -> int:
    feats = F.load()
    if "--check" in argv:
        bad = problems(feats)
        for b in bad:
            print(f"  [rank] {b}")
        print(f"  [rank] {len(feats)} features, {len(bad)} field problem(s)")
        return 1 if bad else 0
    ranked = rank(feats)
    pk = packages(feats, ranked)
    for lane in F.LANES:
        mine = [r for r in ranked if r["lane"] == lane]
        print(f"lane {lane} ({F.LANES[lane]}): {len(mine)} failing, ranked · next package "
              f"{', '.join(pk[lane]['features']) or '—'} ({pk[lane]['points']} points)")
        for r in mine[: int(argv[argv.index('--top') + 1]) if "--top" in argv else 5]:
            print(f"  #{r['rank']:>3} {r['id']}  {r['reason']}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
