import re
import numpy as np
from rank_bm25 import BM25Okapi
from sentence_transformers import SentenceTransformer, CrossEncoder
from data import CHUNKS

IDS = [c["id"] for c in CHUNKS]
TEXTS = [c["text"] for c in CHUNKS]
TEXT_BY_ID = dict(zip(IDS, TEXTS))


def tokenize(text):
    # keeps codes like "hr-204" as ONE token, so exact codes match in BM25
    return re.findall(r"[a-z0-9]+(?:-[a-z0-9]+)*", text.lower())


# ---------- 1. BM25 index ----------
bm25 = BM25Okapi([tokenize(t) for t in TEXTS])

# ---------- 2. Vector index (same chunks) ----------
embedder = SentenceTransformer("all-MiniLM-L6-v2")
EMB = embedder.encode(TEXTS, normalize_embeddings=True)

# ---------- 3. Cross-encoder reranker ----------
reranker = CrossEncoder("cross-encoder/ms-marco-MiniLM-L-6-v2")


def bm25_search(query, k=20):
    scores = bm25.get_scores(tokenize(query))
    return [IDS[i] for i in np.argsort(-scores)[:k]]


def vector_search(query, k=20):
    qv = embedder.encode([query], normalize_embeddings=True)[0]
    sims = EMB @ qv
    return [IDS[i] for i in np.argsort(-sims)[:k]]


def rrf(rank_lists, k=60):
    """Reciprocal Rank Fusion: score = sum of 1/(k + rank) over all lists."""
    scores = {}
    for ranking in rank_lists:
        for rank, doc_id in enumerate(ranking, start=1):
            scores[doc_id] = scores.get(doc_id, 0) + 1.0 / (k + rank)
    return [d for d, _ in sorted(scores.items(), key=lambda x: -x[1])]


def hybrid_search(query, k=20):
    return rrf([bm25_search(query, k), vector_search(query, k)])[:k]


def hybrid_rerank(query, retrieve_k=20, keep=5):
    candidates = hybrid_search(query, retrieve_k)            # top 20
    scores = reranker.predict([(query, TEXT_BY_ID[c]) for c in candidates])
    order = np.argsort(-np.array(scores))[:keep]             # keep top 5
    return [candidates[i] for i in order]