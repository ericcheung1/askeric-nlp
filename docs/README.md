*Old iteration of this app

# Word-Processor-Dot-Com - Text Processing Web App

A lightweight backend-for-frontend (BFF) web application that serves as a client for the [WPaaS](https://github.com/ericcheung1/WPaaS) NLP Inference API. The app provides real‑time sentiment analysis for both standalone text and Reddit posts.

## Architecture

The app runs on a VPS which avoids server spin‑ups on managed hosting platforms. It follows the backend-for-frontend (BFF) pattern using FastAPI. 

The backend handles:
- Reddit content ingestion via PRAW
- Sentiment inference through the [WPaaS](https://github.com/ericcheung1/WPaaS) NLP Inference API
- Server‑side rendering of a Jinja2 index page
- HTMX‑driven updates for dynamic UI without full reloads

## Deployment
- Docker Compose for service orchestration
- GitHub Actions CI/CD pipeline
- Deployed on a single low‑memory VPS
- Caddy handles HTTPS, routing, and reverse proxying
- Communicates directly with the [WPaaS](https://github.com/ericcheung1/WPaaS) API over HTTP

## Technology Stack

- FastAPI: backend routing and request handling
- Jinja2: server‑side HTML templating
- HTMX: dynamic page updates without full reloads
- Tailwind CSS: styling

## APIs & External Services

- PRAW (Python Reddit API Wrapper): fetching Reddit posts and comments
- [WPaaS](https://github.com/ericcheung1/WPaaS) NLP Inference API: provides sentiment analysis predictions in real time
