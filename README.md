## r/AskEricNLP - Reddit and Sentence Analysis

A backend-for-frontend (BFF) web application built with FastAPI that uses natural language processing (NLP) to provide real‑time analysis on both standalone text and Reddit posts.

## File Structure

```
askeric-nlp/
├── app/
│   ├── clients/
│   │   ├── reddit.py               # Authenticates PRAW, gets reddit posts
│   │   └── spaces.py               # Downloads weight files from object store
│   ├── core/
│   │   └── user.py                 # Handles user input, transforms data
│   ├── router/
│   │   └── index.py                # Defines routes used in main page
│   ├── templates/
│   │   ├── index.html
│   │   ├── result_update_r.html
│   │   └── result_update_s.html
│   └── main.py                     # App entry point
└── ml/
    └── sentiment/
        ├── distilbert_fp16_onnx/   # ML weights directory, not included in repo
        │   ├── distilbert_fp16.onnx
        │   └── tokenizer.json
        └── inference.py            # Loads model and handles ML inference
```

## Architecture

The app follows the backend-for-frontend (BFF) pattern using FastAPI. ML model weight files are downloaded from remote object storage and loaded at app start-time.

The backend handles:
- Reddit content ingestion via PRAW (Python Reddit API Wrapper)
- ML model loading and inference using a DistilBERT model
- Server‑side rendering of a Jinja2 index page
- HTMX‑driven updates for dynamic UI without full reloads

## Model(s)

### Sentiment

- DistilBERT [[HuggingFace Model Card](https://huggingface.co/distilbert/distilbert-base-uncased-finetuned-sst-2-english)] for binary sentiment classification
- Weights have been converted to .onnx format and FP16 precision for improved loading and inference speeds
- See `docs/distilbert_onnx/` for script to export .onnx model weights
