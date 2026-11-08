"""Phase 1 reconnaissance: facts about this session's transcript, measured before any pipeline code.

Prints counts, token figures and timestamps only (no conversation content), so the output is safe
to commit. Re-run: python -I evidence/phase1-recon/recon.py
Numbers grow as the session continues; the committed output is the 2026-11-08 01:0x EST snapshot.
"""
import json
import os

SESSION = "0cf9c9ad-b66c-4406-998d-e6e34b8c2e47"
PATH = os.path.join(os.path.expanduser("~"), ".claude", "projects", "C--Claude-Folder", SESSION + ".jsonl")

# App context readings copied from progress/usage.md (time EST, tokens).
READINGS = [("00:20", 127976), ("00:28", 157199), ("00:43:25", 268883), ("00:51:29", 293955), ("00:57:55", 81551)]

rows = [json.loads(line) for line in open(PATH, encoding="utf-8") if line.strip()]
responses = {}  # message.id -> (timestamp, usage), first occurrence wins
order = []
api_requests = 0
boundaries = []
for i, d in enumerate(rows):
    if d.get("type") == "api-request":
        api_requests += 1
    if d.get("type") == "system" and d.get("subtype") == "compact_boundary":
        boundaries.append((i, d))
    m = d.get("message") if isinstance(d.get("message"), dict) else {}
    if m.get("usage") and m.get("id") and m["id"] not in responses:
        responses[m["id"]] = (d.get("timestamp"), m["usage"])
        order.append((i, m["id"]))


def ctx(u):
    return u.get("input_tokens", 0) + u.get("cache_creation_input_tokens", 0) + u.get("cache_read_input_tokens", 0)


print("FACT 1: records in transcript:", len(rows), "| unique responses:", len(responses), "| api-request records:", api_requests)
print("        (one api-request more than responses = the request in flight while this script runs)")

print("FACT 2: compact boundaries:", len(boundaries))
for i, b in boundaries:
    md = b.get("compactMetadata", {})
    print("  at", b.get("timestamp"), "trigger", md.get("trigger"), "preTokens", md.get("preTokens"), "postTokens", md.get("postTokens"), "durationMs", md.get("durationMs"))
    before = [mid for j, mid in order if j < i]
    after = [mid for j, mid in order if j > i]
    last = responses[before[-1]][1]
    print("  last response before: context", ctx(last), "+ output", last.get("output_tokens"), "=", ctx(last) + last.get("output_tokens", 0), "| equals preTokens:", ctx(last) + last.get("output_tokens", 0) == md.get("preTokens"))
    nxt = responses[after[0]][1] if after else None
    if nxt:
        print("  first response after: input", nxt.get("input_tokens"), "cache write", nxt.get("cache_creation_input_tokens"), "cache read", nxt.get("cache_read_input_tokens"))
    between = [r for r in rows[i - 12:i] if r.get("type") in ("api-request", "assistant")]
    print("  api-request or assistant records in the 12 records before the boundary:", [r.get("type") + "@" + str(r.get("timestamp", ""))[11:19] for r in between])

print("FACT 3: app context readings vs the transcript response with the nearest context size (the 00:20 and 00:28 times were written down to the minute only)")
for label, tokens in READINGS:
    best = min(responses.values(), key=lambda tu: abs(ctx(tu[1]) - tokens))
    diff = tokens - ctx(best[1])
    print("  %-9s app %7d | response at %s context %7d | difference %4d (%.2f%%)" % (label, tokens, best[0][11:19], ctx(best[1]), diff, 100.0 * abs(diff) / tokens))

u = responses[order[0][1]][1]
print("FACT 4: usage fields:", sorted(u.keys()))
print("        output_tokens_details:", u.get("output_tokens_details"), "| cache_creation:", u.get("cache_creation"))
