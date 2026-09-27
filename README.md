# askeric-nlp - Reddit & Sentence Analysis App

A FastAPI application for real-time sentiment analysis on standalone text and live Reddit threads. Built with a dynamic HTMX web interface and a dedicated REST API layer for programmatic JSON payloads, the application is designed for throughput and concurrency on minimal production resources.

### Highlights

* **Web & API Access:** Serves an HTMX-powered webpage alongside a REST endpoint for programmatic JSON sentence analysis.
* **Thread-Offloaded Inference:** Runs ML predictions on separate worker threads to keep the main event loop responsive under concurrent load.
* **Lightweight FP16 ONNX Weights:** Uses an FP16-quantized DistilBERT model for low-memory, fast CPU inference.
* **Cached Reddit Pipeline:** Ingests Reddit threads asynchronously via `AsyncPRAW` and caches results in SQLite to bypass redundant processing.

## Built With

* **Backend & API:** FastAPI, Python, SQLite
* **Frontend:** Jinja2, HTMX, Tailwind CSS
* **ML Inference:** ONNX Runtime, Hugging Face Tokenizer
* **External APIs:** AsyncPRAW (Reddit API)
* **Infrastructure & Ops:** Docker, Caddy, Terraform, GitHub Actions

The application follows a Server-Side Rendering (SSR) pattern with HTMX handling dynamic UI state updates. On application startup, model artifacts are fetched from object storage and loaded into memory for immediate inference execution.

## API Documentation

The REST API layer accepts JSON payloads for sentence sentiment analysis. 

* **Interactive OpenAPI Docs:** Available at `/docs` on the production URL.

## File Structure

```
askeric-nlp/
├── app/
│   ├── clients/
│   │   ├── cache.py                # Handles mechanism for caching already processed posts  
│   │   ├── exceptions.py           # Handles exceptions occuring in client modules
│   │   ├── reddit.py               # Connects with AsyncPRAW to get reddit posts
│   │   └── spaces.py               # Connects to object store to download weight files from
│   ├── core/
│   │   ├── api_service.py          # Handles core data transform logic for api side
│   │   └── webpage_service.py      # Handles core user input and data transform logic for the webpage side
│   ├── router/
│   │   ├── api.py                  # Defines routes used in the api layer
│   │   └── webpage.py              # Defines routes used in main text analysis webpage
│   ├── templates/
│   │   ├── error.html
│   │   ├── index.html
│   │   ├── reddit_result.html
│   │   └── sentence_result.html
│   └── main.py                     # App entry point
└── ml/
    └── sentiment/
        ├── distilbert_fp16_onnx/   # ML weights directory, not committed in repo
        │   ├── distilbert_fp16.onnx
        │   └── tokenizer.json
        └── inference.py            # Loads model and handles ML inference
```

## Model & Artifact Details

#### Sentiment

- **Architecture:** DistilBERT ([`distilbert-base-uncased-finetuned-sst-2-english`](https://huggingface.co/distilbert/distilbert-base-uncased-finetuned-sst-2-english)) fine-tuned for binary sentiment classification.
- **Optimization:** Exported to `.onnx` and quantized to FP16 precision for improved loading and CPU inference speed. Model artifacts are downloaded dynamically on startup if not present locally.
- **Export Scripts:** Located in `docs/distilbert_onnx/`.
