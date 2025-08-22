# Document Classifier Showcase

A minimal full-stack demo using FastAPI (backend) and vanilla HTML/CSS/JS (frontend).

- Rule-based classification in Amharic and English
- Extensible training endpoint to add keywords and store samples
- Simple unsupervised clustering demo (TF-IDF + KMeans)

## Quickstart

1. Create venv (optional) and install deps:

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
```

2. Run backend:

```bash
uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
```

- Health: `GET /health`
- Classify: `POST /api/classify` { text, lang: 'am'|'en'|'auto', top_k }
- Train: `POST /api/train` { lang, category, keywords?, samples? }
- Rules: `GET /api/rules`
- Cluster: `POST /api/cluster` { texts: string[], num_clusters }

3. Open frontend:

- Serve `frontend/` (any static server) or use the same port if reverse-proxying. For a quick local test, open `frontend/index.html` directly in your browser or run a simple server:

```bash
python3 -m http.server --directory frontend 8080
```

Then browse to `http://localhost:8080`.

## Notes

- Custom keywords and samples persist under `data/`.
- This is a showcase; replace the rule-based logic or training stubs with ML models later.
- Keep folder structure simple for beginners.
