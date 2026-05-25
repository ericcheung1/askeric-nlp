## Word-Processor-Dot-Com - Text Processing Web App

Prototype Live On: https://www.word-processor-dot-com.site/

A lightweight frontend‑for‑backend (BFF) web application that serves as a client for the [WPaaS](https://github.com/ericcheung1/WPaaS) NLP Inference API. The app provides real‑time sentiment analysis for both standalone text and Reddit posts (via PRAW).

The app runs on a VPS using FastAPI, which avoids server spin‑ups on managed hosting platforms while having a simple Python backend for fetching Reddit content and communicating with the WPaaS NLP API.

## Architecture & Deployment
- Deployed on a single low‑memory VPS
- Caddy handles HTTPS, routing, and reverse proxying 
- Communicates directly with the WPaaS API over HTTP

## Technology Stack

- FastAPI: backend routing and request handling
- Jinja2: server‑side HTML templating
- HTMX: dynamic page updates without full reloads
- Tailwind CSS: styling

## APIs & External Services

- PRAW (Python Reddit API Wrapper): fetching Reddit posts and comments
- [WPaaS](https://github.com/ericcheung1/WPaaS) NLP Inference API: provides sentiment analysis predictions in real time
