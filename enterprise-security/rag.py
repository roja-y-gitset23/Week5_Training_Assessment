import re
from docs import CHUNKS

STOP = {"what", "is", "the", "of", "and", "does", "say", "about", "for", "in", "are",
        "how", "many", "a", "an", "to", "can", "i", "my", "do", "me", "on", "at", "it"}


def tokens(text):
    return set(re.findall(r"[a-z0-9]+", text.lower()))


def retrieve(question, role, k=2, min_hits=2):
    # SECURITY: filter by role BEFORE any scoring, so blocked chunks are never even looked at
    allowed = [c for c in CHUNKS if role in c["allowed_roles"]]

    q = tokens(question) - STOP
    scored = []
    for c in allowed:
        hits = len(q & tokens(c["text"]))
        if hits > 0 and hits >= min(min_hits, len(q)):
            scored.append((hits, c))
    scored.sort(key=lambda x: -x[0])
    return [c for _, c in scored[:k]]


def answer_rag(question, role):
    results = retrieve(question, role)
    if not results:
        return "I don't know"
    top = results[0]
    return f"{top['text']} (source: {top['source']}, {top['section']})"