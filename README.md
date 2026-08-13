## r/AskEricNLP - Reddit and Sentence Analysis

A web application built with FastAPI that uses natural language processing (NLP) to provide real‑time sentiment analysis on both standalone text and Reddit posts.

## File Structure

```
askeric-nlp/
├── app/
│   ├── clients/
│   │   ├── exceptions.py           # Handles exceptions occuring in client modules
│   │   ├── reddit.py               # Connects with PRAW to get reddit posts
│   │   └── spaces.py               # Connects to object store to download weight files from
│   ├── core/
│   │   └── user.py                 # Handles core user input and data transform logic
│   ├── router/
│   │   └── text_analysis.py        # Defines routes used in main text analysis page
│   ├── templates/
│   │   ├── error.html
│   │   ├── index.html
│   │   ├── reddit_result.html
│   │   └── sentence_result.html
│   └── main.py                     # App entry point
└── ml/
    └── sentiment/
        ├── distilbert_fp16_onnx/   # ML weights directory, not included in repo
        │   ├── distilbert_fp16.onnx
        │   └── tokenizer.json
        └── inference.py            # Loads model and handles ML inference
```

## Architecture

The app follows Server-Side Rendering (SSR) pattern using FastAPI. ML model weight files are downloaded from remote object storage and loaded at app start-time.

The backend handles:
- Reddit content ingestion via PRAW (Python Reddit API Wrapper)
- ML model loading and inference using a DistilBERT model
- Rendering of a Jinja2 HTML index page
- HTMX‑driven updates for dynamic UI without full reloads

## Model(s)

### Sentiment

- DistilBERT [[HuggingFace Model Card](https://huggingface.co/distilbert/distilbert-base-uncased-finetuned-sst-2-english)] for binary sentiment classification
- Weights have been converted to .onnx format and FP16 precision for improved loading and inference speeds
- See `docs/distilbert_onnx/` for script to export .onnx model weights
