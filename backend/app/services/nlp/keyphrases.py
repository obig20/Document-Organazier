from typing import List
import re
from collections import Counter

from app.services.nlp.amharic_tokenizer import amharic_tokenizer


def extract_key_phrases(text: str, top_k: int = 10) -> List[str]:
	"""Naive key phrase extraction using token frequencies for both English and Amharic."""
	if not text:
		return []

	# English tokenization (very simple)
	eng_tokens = re.findall(r"[A-Za-z][A-Za-z\-']+", text)
	eng_tokens = [t.lower() for t in eng_tokens if len(t) >= 3]

	# Amharic meaningful words
	amh_tokens = amharic_tokenizer.extract_meaningful_words(text)

	counts = Counter(eng_tokens + amh_tokens)
	return [w for w, _ in counts.most_common(top_k)]


