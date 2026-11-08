import json, glob, os, collections
base = os.path.expanduser("~/.claude/projects/C--Claude-Folder")
files = sorted(glob.glob(base + "/*.jsonl"))

global_ids = collections.Counter()
info = {}
for f in files:
    sid = os.path.basename(f)[:8]
    rows = 0; per_id = {}; uuids = set(); ts = []; ctrue = 0; ckey = 0; first_types = []
    out_all = cr_all = 0
    with open(f, encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if not line: continue
            try: d = json.loads(line)
            except Exception: continue
            if len(first_types) < 4: first_types.append(d.get("type"))
            if d.get("uuid"): uuids.add(d["uuid"])
            if d.get("timestamp"): ts.append(d["timestamp"])
            if "isCompactSummary" in d:
                ckey += 1
                if d["isCompactSummary"] is True: ctrue += 1
            m = d.get("message")
            if isinstance(m, dict) and m.get("usage"):
                rows += 1
                u = m["usage"]; mid = m.get("id") or d.get("requestId")
                out_all += u.get("output_tokens", 0); cr_all += u.get("cache_read_input_tokens", 0)
                prev = per_id.get(mid, (0, 0))
                per_id[mid] = (max(prev[0], u.get("output_tokens", 0)), max(prev[1], u.get("cache_read_input_tokens", 0)))
    for k in per_id: global_ids[k] += 1
    info[sid] = dict(rows=rows, uniq=len(per_id), out_all=out_all, out_dedup=sum(v[0] for v in per_id.values()),
                     cr_all=cr_all, cr_dedup=sum(v[1] for v in per_id.values()), ctrue=ctrue, ckey=ckey,
                     uuids=uuids, in_order=(ts == sorted(ts)), tmin=min(ts)[:16] if ts else "", tmax=max(ts)[:16] if ts else "",
                     first_types=first_types)

print("TEST 1: is usage repeated across rows of the same API response?")
print(f"{'sess':9}{'usage_rows':>11}{'unique_resp':>12}{'out_naive':>12}{'out_dedup':>12}{'cacheread_naive':>17}{'cacheread_dedup':>17}")
T = collections.Counter()
for s, i in info.items():
    print(f"{s:9}{i['rows']:>11}{i['uniq']:>12}{i['out_all']:>12}{i['out_dedup']:>12}{i['cr_all']:>17}{i['cr_dedup']:>17}")
    for k in ("rows","uniq","out_all","out_dedup","cr_all","cr_dedup"): T[k] += i[k]
print(f"{'TOTAL':9}{T['rows']:>11}{T['uniq']:>12}{T['out_all']:>12}{T['out_dedup']:>12}{T['cr_all']:>17}{T['cr_dedup']:>17}")
dup_across = sum(1 for k, c in global_ids.items() if c > 1)
print(f"\nTEST 2: API responses that appear in MORE THAN ONE session file: {dup_across} of {len(global_ids)}")

print("\nTEST 3: was 69d5f5a4 -> dd7e16ba really a /clear?")
a, b, c = info["69d5f5a4"], info["dd7e16ba"], info["84e63a2d"]
print(f"  dd7e16ba rows whose uuid also exists in 69d5f5a4: {len(b['uuids'] & a['uuids'])} of {len(b['uuids'])}")
print(f"  84e63a2d rows whose uuid also exists in dd7e16ba: {len(c['uuids'] & b['uuids'])} of {len(c['uuids'])}")
for s in ("69d5f5a4","dd7e16ba","84e63a2d"):
    i = info[s]; print(f"  {s}: true time span {i['tmin']} -> {i['tmax']}, rows in time order: {i['in_order']}, first record types: {i['first_types']}")

print("\nTEST 4: compaction flag, key present vs actually true:")
print("  key present:", sum(i['ckey'] for i in info.values()), " value true:", sum(i['ctrue'] for i in info.values()))
