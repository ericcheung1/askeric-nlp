# askeric-nlp - Reddit & Sentence Analysis App

A FastAPI application for real-time natural language processing (NLP) analysis on Reddit threads and standalone text. Built with a dynamic HTMX web interface and a dedicated REST API layer for programmatic JSON payloads, the application is designed for throughput and concurrency on minimal production resources.

Current NLP taks supported:
- Sentiment Analysis
- Keyword Extraction

## Built With

* **Backend & API:** FastAPI, Python, SQLite
* **Frontend:** Jinja2, HTMX, Tailwind CSS
* **External APIs:** AsyncPRAW (Reddit API)
* **Infrastructure & Ops:** Docker, Caddy, Terraform, Digital Ocean Droplet, GitHub Actions

The application follows a Server-Side Rendering (SSR) pattern with HTMX handling dynamic UI state updates. On application startup, model artifacts are fetched from object storage and loaded into memory for immediate inference execution.

## API Documentation

The REST API layer accepts JSON payloads for sentence sentiment analysis. 

* **Interactive OpenAPI Docs:** Available at `/docs` on the production URL.

## File Structure

```
askeric-nlp/
├── app/
│   ├── clients/
│   │   ├── cache.py                    # Handles mechanism for caching processed posts
│   │   ├── exception.py                # Handles exceptions occuring in clients modules
│   │   └── reddit.py                   # Handles connection with AyncPraw to parse Reddit posts
│   ├── core/
│   │   ├── webpage_service/
│   │   │   ├── common.py               # Shared operations between Reddit and sentence requests
│   │   │   ├── reddit_requests.py      # Operations related to Reddit requests
│   │   │   └── sentence_requests.py    # Operations related to sentence requests
│   │   ├── api_service.py              # API related operations
│   │   ├── keyword.py                  # Handles operating keyword extraction model
│   │   └── sentiment.py                # Handles operating sentiment model
│   ├── router/
│   │   ├── api.py                      # Defines routes used in API layer
│   │   └── webpage.py                  # Defines routes used in webpage layer
│   ├── templates/
│   │   ├── error.html
│   │   ├── index.html
│   │   ├── reddit_result.html
│   │   └── sentence_result.html
│   └── main.py                         # App entrypoint
└── ml/
    ├── nltk/
    │   ├── sentiment/
    │   │   └── vader_lexicon.txt
    │   └── load.py
    └── yake/
        └── load.py
```

## Model & Artifact Details

#### Sentiment

- **Model:** NLTK Vader ([`Vader`](https://www.nltk.org/_modules/nltk/sentiment/vader.html)) is a lexicon- and rule-based sentiment analysis tool designed specifically to catch emotions in short, informal text like social media posts, reviews, and headlines

```
Hutto, C.J. & Gilbert, E.E. (2014). VADER: A Parsimonious Rule-based Model for
Sentiment Analysis of Social Media Text. Eighth International Conference on
Weblogs and Social Media (ICWSM-14). Ann Arbor, MI, June 2014.
```

#### Keywords

- **Model:** Yake ([`Yake!`](https://github.com/INESCTEC/yake)) a lightweight unsupervised automatic keyword extraction method