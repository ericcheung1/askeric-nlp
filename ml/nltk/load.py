import logging
from pathlib import Path

import nltk
from nltk.sentiment.vader import SentimentIntensityAnalyzer

logger = logging.getLogger(__name__)

VADER_PATH = Path("ml/nltk/sentiment/vader_lexicon.txt")
nltk.data.path.append(VADER_PATH)


def sentiment_load_model():
    """Loads nltk vader sentiment model"""
    try:
        return SentimentIntensityAnalyzer(lexicon_file=f"file://{VADER_PATH.resolve()}")
    except Exception as e:
        logger.critical(f"{e!s} in 'sentiment_load_model'")
        raise FileNotFoundError
