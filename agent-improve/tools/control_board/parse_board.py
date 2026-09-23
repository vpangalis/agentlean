"""Extract the step plan from the generated board.html. No hand-typed status."""
import re, html, json, sys

def parse(path):
    h = open(path, encoding='utf-8').read()
    out = {"steps": [], "vertical": []}

    m = re.search(r'(\d+) of (\d+) spine steps landed\s*·\s*(\d+)%', h)
    out["landed"], out["total"], out["pct"] = (int(m.group(1)), int(m.group(2)), int(m.group(3))) if m else (0,0,0)
    m = re.search(r'(\d+) of (\d+) BUILT markers still open', h)
    out["markers_open"], out["markers_total"] = (int(m.group(1)), int(m.group(2))) if m else (0,0)
    m = re.search(r'last spine step landed:\s*<b>([^<]+)</b>', h)
    out["last_step"] = m.group(1) if m else None

    # every step, including ones that landed long ago and carry no card
    all_steps = {}
    mm = re.search(r'Landed.{0,40}?(\d+)\s*steps(.{0,12000})', h, re.S)
    if mm:
        seg = re.sub(r'<[^>]+>', '\n', html.unescape(mm.group(2)))
        for n, t in re.findall(r'(\d+\.\d+)\s*\u2014\s*([^\n]{2,90})', seg):
            all_steps.setdefault(n, {"num": n, "title": t.strip(), "status": "done"})
    out["all_steps"] = all_steps

    seen = set()
    zones = dict()
    for num, z in re.findall(r'<div class="bstep">([^<]*)</div>.*?<span class="bzone">([^<]*)</span>', h, re.S):
        n = num.replace('\u25b6','').strip()
        zones.setdefault(n, z.strip())
    for cls, payload in re.findall(r'<div class="((?:bcard|vrow)[^"]*)" data-b="([^"]*)"', h):
        body = html.unescape(payload)
        t = re.search(r'<div class="bt">(.*?)</div>', body, re.S)
        if not t: continue
        title = html.unescape(re.sub(r'<[^>]+>', '', t.group(1))).strip()
        num = title.split('—')[0].strip()
        rows = {}
        for lbl, val in re.findall(r'<div class="br[^"]*"><span>(.*?)</span>(.*?)</div>', body, re.S):
            rows[re.sub(r'<[^>]+>','',lbl).strip()] = html.unescape(re.sub(r'<[^>]+>','',val)).strip()
        status = [w for w in cls.split() if w not in ('bcard','vrow')]
        rec = {
            "num": num,
            "title": title.split('—',1)[1].strip() if '—' in title else title,
            "status": status[0] if status else "open",
            "band": rows.get('band','').split('—')[0].strip(),
            "band_full": rows.get('band',''),
            "done_when": rows.get('done when',''),
            "precondition": rows.get('precondition',''),
            "verify": rows.get('verify',''),
            "zone": zones.get(num, ""),
        }
        key = (cls.startswith('vrow'), num)
        if key in seen: continue
        seen.add(key)
        (out["vertical"] if cls.startswith('vrow') else out["steps"]).append(rec)
    for r in out["steps"]:
        out["all_steps"][r["num"]] = {"num": r["num"], "title": r["title"], "status": r["status"]}
    return out

if __name__ == '__main__':
    d = parse(sys.argv[1] if len(sys.argv)>1 else 'board.html')
    json.dump(d, open('gen/board_data.json','w'), indent=1)
    print(f'{d["landed"]}/{d["total"]} ({d["pct"]}%) · markers {d["markers_open"]}/{d["markers_total"]} · last {d["last_step"]}')
    print(f'plan steps: {len(d["steps"])} · vertical: {len(d["vertical"])}')
    from collections import Counter
    print('statuses:', dict(Counter(s["status"] for s in d["steps"])))
    print('bands:', dict(Counter(s["band"] for s in d["steps"])))
    print('vertical:', [(s["num"], s["status"]) for s in d["vertical"]])
