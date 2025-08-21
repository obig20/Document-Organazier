"""
Amharic text tokenization and preprocessing utilities
Handles Geez script, Ethiopian-specific text processing
"""
import re
import unicodedata
from typing import List, Optional, Dict, Set
import logging

logger = logging.getLogger(__name__)

class AmharicTokenizer:
    """Tokenizer specifically designed for Amharic text"""
    
    def __init__(self):
        # Geez (Amharic) Unicode ranges
        self.geez_range = (0x1200, 0x137F)  # Main Geez block
        self.geez_supplement_range = (0x1380, 0x139F)  # Geez Supplement
        self.geez_extended_range = (0x2D80, 0x2DDF)  # Geez Extended
        
        # Common Amharic punctuation marks
        self.amharic_punctuation = {
            '፡': '.',    # Wordspace
            '።': '.',    # Full stop
            '፣': ',',    # Comma  
            '፤': ';',    # Semicolon
            '፥': ':',    # Colon
            '፦': '::',   # Preface colon
            '፧': '?',    # Question mark
            '፨': '¶'     # Paragraph separator
        }
        
        # Amharic digit mappings
        self.amharic_digits = {
            '፩': '1', '፪': '2', '፫': '3', '፬': '4', '፭': '5',
            '፮': '6', '፯': '7', '፰': '8', '፱': '9', '፲': '10',
            '፳': '20', '፴': '30', '፵': '40', '፶': '50',
            '፷': '60', '፸': '70', '፹': '80', '፺': '90', '፻': '100'
        }
        
        # Common Amharic stop words
        self.stop_words = {
            'እና', 'ወይም', 'ግን', 'ነገር', 'ወደ', 'ከ', 'በ', 'ለ', 'እ', 'ን',
            'ት', 'ይ', 'ው', 'ም', 'ር', 'ስ', 'አ', 'ዎ', 'ች', 'ሽ', 'ሀ', 'ላ',
            'ከሆነ', 'ከዚህ', 'ከዚያ', 'በዚህ', 'በዚያ', 'ስለ', 'ባህሪ', 'እንደ',
            'መሰረት', 'አንደ', 'የሚል', 'ያለ', 'ያለው', 'እኔ', 'አንተ', 'እሱ',
            'እሷ', 'እኛ', 'አንትም', 'እነሱ', 'ሁሉ', 'ሁሉም'
        }
        
    def is_geez_script(self, char: str) -> bool:
        """Check if character is part of Geez script"""
        ord_char = ord(char)
        return (
            self.geez_range[0] <= ord_char <= self.geez_range[1] or
            self.geez_supplement_range[0] <= ord_char <= self.geez_supplement_range[1] or
            self.geez_extended_range[0] <= ord_char <= self.geez_extended_range[1]
        )
    
    def normalize_text(self, text: str) -> str:
        """Normalize Amharic text"""
        if not text:
            return ""
        
        # Unicode normalization
        text = unicodedata.normalize('NFC', text)
        
        # Normalize punctuation
        for amh_punct, eng_punct in self.amharic_punctuation.items():
            text = text.replace(amh_punct, eng_punct)
        
        # Convert Amharic digits to Arabic numerals
        for amh_digit, arab_digit in self.amharic_digits.items():
            text = text.replace(amh_digit, arab_digit)
        
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text).strip()
        
        return text
    
    def tokenize(self, text: str, remove_punctuation: bool = False, 
                 remove_stop_words: bool = False) -> List[str]:
        """Tokenize Amharic text into words"""
        if not text:
            return []
        
        # Normalize text first
        text = self.normalize_text(text)
        
        # Split by whitespace and common punctuation
        # Amharic words can be complex due to morphology
        tokens = re.findall(r'[\w\u1200-\u137F\u1380-\u139F\u2D80-\u2DDF]+|[^\w\s]', text)
        
        if remove_punctuation:
            # Keep only tokens that contain alphanumeric or Geez characters
            tokens = [token for token in tokens if re.search(r'[\w\u1200-\u137F\u1380-\u139F\u2D80-\u2DDF]', token)]
        
        if remove_stop_words:
            tokens = [token for token in tokens if token.lower() not in self.stop_words]
        
        return tokens
    
    def extract_words(self, text: str) -> List[str]:
        """Extract only Amharic words (no punctuation)"""
        return self.tokenize(text, remove_punctuation=True, remove_stop_words=False)
    
    def extract_meaningful_words(self, text: str) -> List[str]:
        """Extract meaningful Amharic words (no stop words)"""
        return self.tokenize(text, remove_punctuation=True, remove_stop_words=True)
    
    def sentence_split(self, text: str) -> List[str]:
        """Split text into sentences"""
        if not text:
            return []
        
        text = self.normalize_text(text)
        # Split by sentence-ending punctuation
        sentences = re.split(r'[።!?፧]+', text)
        sentences = [s.strip() for s in sentences if s.strip()]
        return sentences
    
    def get_word_frequency(self, text: str, min_length: int = 2) -> Dict[str, int]:
        """Get frequency count of words in text"""
        words = self.extract_meaningful_words(text)
        word_freq = {}
        
        for word in words:
            if len(word) >= min_length:
                word_freq[word] = word_freq.get(word, 0) + 1
        
        return dict(sorted(word_freq.items(), key=lambda x: x[1], reverse=True))
    
    def detect_language(self, text: str) -> Dict[str, float]:
        """Simple language detection for Amharic vs other languages"""
        if not text:
            return {"amharic": 0.0, "other": 0.0}
        
        total_chars = len(text)
        geez_chars = sum(1 for char in text if self.is_geez_script(char))
        
        amharic_ratio = geez_chars / total_chars if total_chars > 0 else 0
        
        return {
            "amharic": amharic_ratio,
            "other": 1 - amharic_ratio
        }

# Singleton instance
amharic_tokenizer = AmharicTokenizer()
