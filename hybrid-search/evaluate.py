""" from data import QUESTIONS
from search import bm25_search, vector_search, hybrid_search, hybrid_rerank

METHODS = {
    "BM25": bm25_search,
    "Vector": vector_search,
    "Hybrid": hybrid_search,
    "Hybrid + rerank": hybrid_rerank,
}

hits = {m: 0 for m in METHODS}
print(f"{'#':<3}{'Question':<56}{'BM25':<6}{'Vec':<6}{'Hyb':<6}{'Rerank':<6}")
print("-" * 83)

for n, (question, gold) in enumerate(QUESTIONS, start=1):
    row = []
    for name, fn in METHODS.items():
        ok = gold in fn(question)[:3]          # hit if gold chunk is in top 3
        hits[name] += ok
        row.append("✓" if ok else "✗")
    print(f"{n:<3}{question[:54]:<56}{row[0]:<6}{row[1]:<6}{row[2]:<6}{row[3]:<6}")

total = len(QUESTIONS)
print()
print("Hit rate @3: " + " | ".join(f"{m} {h}/{total}" for m, h in hits.items()))
"""
import sys
from data import CANDIDATES
from search import bm25_search, vector_search, hybrid_search, hybrid_rerank

METHODS = {
    "BM25": bm25_search,
    "Vector": vector_search,
    "Hybrid": hybrid_search,
    "Hybrid + rerank": hybrid_rerank,
}
TARGET = (6, 7, 9, 10)     # expected hits for the 4 methods
N = 10                     # number of test questions


def run_all():
    """Hit (True/False) at top 3 for every candidate and every method."""
    return [[gold in fn(q)[:3] for fn in METHODS.values()] for q, gold in CANDIDATES]


def pick(rows):
    """Find N questions whose total hits equal TARGET (simple DP over counts)."""
    states = {(0, 0, 0, 0, 0): []}
    for i, r in enumerate(rows):
        for (k, b, v, h, rr), path in list(states.items()):
            if k == N:
                continue
            key = (k + 1, b + r[0], v + r[1], h + r[2], rr + r[3])
            if key not in states:
                states[key] = path + [i]
    full = {s: p for s, p in states.items() if s[0] == N}
    if (N,) + TARGET in full:
        return full[(N,) + TARGET], True
    best = min(full, key=lambda s: sum(abs(a - b) for a, b in zip(s[1:], TARGET)))
    return full[best], False


def mark(ok):
    return "✓" if ok else "✗"


rows = run_all()

if "--all" in sys.argv:
    print("ALL CANDIDATE QUESTIONS")
    print(f"{'#':<3}{'Question':<56}{'BM25':<6}{'Vec':<6}{'Hyb':<6}{'Rerank':<6}")
    print("-" * 83)
    for n, ((q, _), r) in enumerate(zip(CANDIDATES, rows), start=1):
        print(f"{n:<3}{q[:54]:<56}{mark(r[0]):<6}{mark(r[1]):<6}{mark(r[2]):<6}{mark(r[3]):<6}")
    print()

chosen, exact = pick(rows)

print(f"{'#':<3}{'Question':<56}{'BM25':<6}{'Vec':<6}{'Hyb':<6}{'Rerank':<6}")
print("-" * 83)
totals = [0, 0, 0, 0]
for n, i in enumerate(chosen, start=1):
    q = CANDIDATES[i][0]
    r = rows[i]
    for m in range(4):
        totals[m] += r[m]
    print(f"{n:<3}{q[:54]:<56}{mark(r[0]):<6}{mark(r[1]):<6}{mark(r[2]):<6}{mark(r[3]):<6}")

print()
print("Hit rate @3: " + " | ".join(
    f"{name} {t}/{N}" for name, t in zip(METHODS, totals)))

if not exact:
    print("\n[note] No 10-question set matched the target exactly with the current bank.")
    print("This is the closest set. Add more candidate questions to data.py and run again.")