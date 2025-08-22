import os
from typing import Dict

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .categories import CLASSIFICATION_CATEGORIES
from .classifier import RuleBasedClassifier
from .models import (
    ClassificationRequest,
    ClassificationResponse,
    ClassificationResult,
    TrainRequest,
    TrainResponse,
    ClusterRequest,
    ClusterResponse,
)
from .ml_pipeline import cluster_texts


app = FastAPI(title="Document Classifier Showcase", version="0.1.0")

# CORS for all origins in showcase
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

DATA_DIR = os.path.join(os.getcwd(), "data")
classifier = RuleBasedClassifier(categories=CLASSIFICATION_CATEGORIES, data_dir=DATA_DIR)


@app.get("/health")
async def health() -> Dict[str, str]:
    return {"status": "ok"}


@app.get("/api/categories")
async def get_categories() -> Dict[str, Dict[str, list]]:
    return CLASSIFICATION_CATEGORIES


@app.get("/api/rules")
async def get_rules() -> Dict[str, Dict[str, list]]:
    return classifier.get_merged_rules()


@app.post("/api/classify", response_model=ClassificationResponse)
async def classify(req: ClassificationRequest) -> ClassificationResponse:
    lang = req.lang
    if lang == 'auto':
        lang = classifier.detect_language(req.text)
    results = classifier.classify(req.text, lang, top_k=req.top_k)
    api_results = [ClassificationResult(category=c, score=float(s)) for c, s in results]
    return ClassificationResponse(lang_detected=lang, results=api_results)


@app.post("/api/train", response_model=TrainResponse)
async def train(req: TrainRequest) -> TrainResponse:
    added = 0
    stored = 0
    if req.keywords:
        added = classifier.add_keywords(req.lang, req.category, req.keywords)
    if req.samples:
        stored = classifier.store_samples(req.lang, req.samples)
    return TrainResponse(
        message="Training data accepted (keywords appended, samples stored)",
        added_keywords_count=added,
        stored_samples_count=stored,
    )


@app.post("/api/cluster", response_model=ClusterResponse)
async def cluster(req: ClusterRequest) -> ClusterResponse:
    labels, top_terms, params = cluster_texts(req.texts, num_clusters=req.num_clusters, max_features=req.max_features)
    return ClusterResponse(labels=labels, top_terms=top_terms, params=params)