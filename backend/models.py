from typing import List, Optional, Dict, Any
from pydantic import BaseModel


class ClassificationRequest(BaseModel):
    text: str
    lang: str = 'auto'  # 'am', 'en', or 'auto'
    top_k: int = 3


class ClassificationResult(BaseModel):
    category: str
    score: float


class ClassificationResponse(BaseModel):
    lang_detected: str
    results: List[ClassificationResult]


class TrainRequest(BaseModel):
    lang: str
    category: str
    keywords: Optional[List[str]] = None
    samples: Optional[List[str]] = None


class TrainResponse(BaseModel):
    message: str
    added_keywords_count: int = 0
    stored_samples_count: int = 0


class ClusterRequest(BaseModel):
    texts: List[str]
    num_clusters: int = 3
    max_features: int = 5000


class ClusterResponse(BaseModel):
    labels: List[int]
    top_terms: List[List[str]]
    params: Dict[str, Any]