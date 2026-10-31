# Changelog

All notable changes to this project will be documented in this file.

## - [v0.1.6] 2026-10-31

### Added
- Yake model for keyword extraction

## - [v0.1.5] 2026-10-11 and 2026-10-12

### Changed
- Swap to NLTK Vader from Distilbert for sentiment analysis

### Added
- Pre-analyzed Reddit posts loaded into cache at startup

## - [v0.1.4] 2026-10-05

### Changed
- Refactor source code to organize by functionality (sentence analysis, Reddit analysis, API layer)

## - [v0.1.3] 2026-09-30

### Changed
- Distilbert sentiment model loading and inference offloaded to separate Python process via multiprocessing library

## - [v0.1.2] 2026-09-27

### Added
- Dynamic version number display at bottom of webpage that references version number in pyproject.toml

## - [v0.1.1] 2026-09-27

### Added
- Sentiment analysis API layer for programatic access to sentiment model

## - [v0.1.0] 2026-09-21

### Changed

- UI overhaul

## - [v0.0.5] 2026-09-02

### Changed
- Swap from PRAW to AsyncPRAW to utilize FastAPI's async/await event loop architecture

## - [v0.0.4] 2026-08-30

### Changed
- Refactor as a monolithic app with ML model weights loading form same repo
- See `docs/README.md` for old design of this app 
