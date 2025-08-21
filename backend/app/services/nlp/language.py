from typing import Tuple

from app.services.nlp.amharic_tokenizer import amharic_tokenizer


def detect_language(text: str) -> Tuple[str, float]:
	"""Detect language between Amharic and English using heuristic ratios.

	Returns tuple of (language, confidence).
	"""
	if not text or not text.strip():
		return "unknown", 0.0

	r = amharic_tokenizer.detect_language(text)
	amharic_ratio = r.get("amharic", 0.0)
	other_ratio = r.get("other", 0.0)

	# Heuristic thresholds
	if amharic_ratio >= 0.3:
		return "amharic", round(amharic_ratio, 3)
	if other_ratio >= 0.7:
		return "english", round(other_ratio, 3)
	# Fallback: choose higher ratio
	if amharic_ratio >= other_ratio:
		return "amharic", round(amharic_ratio, 3)
	return "english", round(other_ratio, 3)


