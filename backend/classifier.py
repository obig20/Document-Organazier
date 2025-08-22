import json
import os
import re
from typing import Dict, List, Tuple


ETHIOPIC_BLOCK_RE = re.compile(r"[\u1200-\u137F]")


class RuleBasedClassifier:
    def __init__(self, categories: Dict[str, Dict[str, List[str]]], data_dir: str = "data"):
        self.default_categories = categories
        self.data_dir = data_dir
        os.makedirs(self.data_dir, exist_ok=True)
        self.custom_rules_path = os.path.join(self.data_dir, "custom_rules.json")
        self.training_samples_path = os.path.join(self.data_dir, "training_samples.json")
        self.custom_categories = self._load_custom_rules()

    def _load_custom_rules(self) -> Dict[str, Dict[str, List[str]]]:
        if not os.path.exists(self.custom_rules_path):
            return {lang: {} for lang in self.default_categories.keys()}
        try:
            with open(self.custom_rules_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            # Ensure structure for both languages exists
            for lang in self.default_categories.keys():
                data.setdefault(lang, {})
            return data
        except Exception:
            return {lang: {} for lang in self.default_categories.keys()}

    def _save_custom_rules(self) -> None:
        with open(self.custom_rules_path, "w", encoding="utf-8") as f:
            json.dump(self.custom_categories, f, ensure_ascii=False, indent=2)

    def _save_training_samples(self, lang: str, samples: List[str]) -> None:
        db = {}
        if os.path.exists(self.training_samples_path):
            try:
                with open(self.training_samples_path, "r", encoding="utf-8") as f:
                    db = json.load(f)
            except Exception:
                db = {}
        db.setdefault(lang, [])
        db[lang].extend(samples)
        with open(self.training_samples_path, "w", encoding="utf-8") as f:
            json.dump(db, f, ensure_ascii=False, indent=2)

    def get_merged_rules(self) -> Dict[str, Dict[str, List[str]]]:
        merged: Dict[str, Dict[str, List[str]]] = {}
        for lang, cats in self.default_categories.items():
            merged[lang] = {}
            # default first
            for cat, kws in cats.items():
                merged[lang][cat] = list(dict.fromkeys(kws))
            # then custom additions
            for cat, kws in self.custom_categories.get(lang, {}).items():
                merged[lang].setdefault(cat, [])
                merged[lang][cat].extend(k for k in kws if k not in merged[lang][cat])
        return merged

    def detect_language(self, text: str) -> str:
        # Very naive: Ethiopic block => 'am', else 'en'
        if ETHIOPIC_BLOCK_RE.search(text):
            return 'am'
        return 'en'

    def _normalize_text(self, text: str, lang: str) -> str:
        if lang == 'en':
            return text.lower()
        # For Amharic keep as-is; could add normalization later
        return text

    def _score_category(self, text: str, keywords: List[str], lang: str) -> int:
        normalized_text = self._normalize_text(text, lang)
        score = 0
        for kw in keywords:
            if lang == 'en':
                # basic word/phrase match in lowercase
                kw_norm = kw.lower()
                if kw_norm in normalized_text:
                    score += 1
            else:
                # substring match for amharic terms
                if kw in normalized_text:
                    score += 1
        return score

    def classify(self, text: str, lang: str, top_k: int = 3) -> List[Tuple[str, int]]:
        rules = self.get_merged_rules().get(lang, {})
        scored: List[Tuple[str, int]] = []
        for category, keywords in rules.items():
            s = self._score_category(text, keywords, lang)
            if s > 0:
                scored.append((category, s))
        scored.sort(key=lambda x: x[1], reverse=True)
        return scored[:top_k]

    def add_keywords(self, lang: str, category: str, keywords: List[str]) -> int:
        if not keywords:
            return 0
        self.custom_categories.setdefault(lang, {})
        self.custom_categories[lang].setdefault(category, [])
        existing = set(self.custom_categories[lang][category])
        added = 0
        for kw in keywords:
            if kw not in existing:
                self.custom_categories[lang][category].append(kw)
                existing.add(kw)
                added += 1
        self._save_custom_rules()
        return added

    def store_samples(self, lang: str, samples: List[str]) -> int:
        if not samples:
            return 0
        self._save_training_samples(lang, samples)
        return len(samples)