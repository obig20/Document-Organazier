from collections import Counter
from typing import List, Tuple, Dict, Any, Set
import re

TOKEN_RE = re.compile(r"\w+", re.UNICODE)


def _tokenize(text: str) -> List[str]:
    return TOKEN_RE.findall(text.lower())


def _build_vocab(texts: List[str], max_features: int) -> List[str]:
    freq = Counter()
    for t in texts:
        freq.update(_tokenize(t))
    most_common = [w for w, _ in freq.most_common(max_features)]
    return most_common


def _doc_tokens(text: str, vocab: Set[str]) -> Set[str]:
    return set(tok for tok in _tokenize(text) if tok in vocab)


def _jaccard(a: Set[str], b: Set[str]) -> float:
    if not a and not b:
        return 1.0
    if not a or not b:
        return 0.0
    inter = len(a & b)
    union = len(a | b)
    if union == 0:
        return 0.0
    return inter / union


def _top_terms(cluster_docs: List[List[str]], top_n: int = 10) -> List[str]:
    c = Counter()
    for toks in cluster_docs:
        c.update(toks)
    return [w for w, _ in c.most_common(top_n)]


def cluster_texts(texts: List[str], num_clusters: int = 3, max_features: int = 5000) -> Tuple[List[int], List[List[str]], Dict[str, Any]]:
    if not texts:
        return [], [], {"num_clusters": num_clusters, "max_features": max_features, "algo": "jaccard-seed"}

    n_clusters = max(1, min(num_clusters, len(texts)))

    vocab_list = _build_vocab(texts, max_features)
    vocab = set(vocab_list)

    token_lists: List[List[str]] = [_tokenize(t) for t in texts]
    token_sets: List[Set[str]] = [_doc_tokens(t, vocab) for t in texts]

    # Seed clusters with first n documents
    centroid_sets: List[Set[str]] = []
    cluster_docs_idx: List[List[int]] = []
    labels: List[int] = [-1] * len(texts)

    for i in range(n_clusters):
        centroid_sets.append(set(token_sets[i]))
        cluster_docs_idx.append([i])
        labels[i] = i

    # Assign remaining docs
    for i in range(n_clusters, len(texts)):
        sims = [ _jaccard(token_sets[i], centroid) for centroid in centroid_sets ]
        best = max(range(n_clusters), key=lambda k: sims[k])
        labels[i] = best
        cluster_docs_idx[best].append(i)
        # Update centroid as union set
        centroid_sets[best] |= token_sets[i]

    # Build top terms per cluster
    top_terms: List[List[str]] = []
    for idxs in cluster_docs_idx:
        docs_tokens = [token_lists[j] for j in idxs]
        top_terms.append(_top_terms(docs_tokens, top_n=10))

    params = {"num_clusters": n_clusters, "max_features": max_features, "algo": "jaccard-seed"}
    return labels, top_terms, params