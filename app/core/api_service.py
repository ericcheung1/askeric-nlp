import logging

import numpy as np
from pydantic import BaseModel

logger = logging.getLogger(__name__)


class Text(BaseModel):
    """Represents a single piece of text"""

    id: str | None = None
    text: str


class SentenceInput(BaseModel):
    """Represents a whole input payload with list of texts"""

    id: str | None = None
    inputs: list[Text]


class SentimentResult(BaseModel):
    """Represents a result for analysis on a single piece of text"""

    id: str | None = None
    text: str
    classification: str
    confidence: dict[str, float]


class SentenceOutput(BaseModel):
    """Represents an outgoing output payload with list of results"""

    id: str | None = None
    sentiment: list[SentimentResult]


def clean_sentence_input(sentence_input: SentenceInput):
    """Lowercase and strip text in sentence input"""
    for item in sentence_input.inputs:
        item.text = item.text.lower().strip()

    logger.debug("Cleaned input: %s", sentence_input.inputs)


def prepare_model_inputs(sentence_input: SentenceInput):
    """Splits inputs into texts and ids"""

    texts = []
    ids = []

    for item in sentence_input.inputs:
        texts.append(item.text)
        ids.append(item.id)

    logger.debug("Input texts: %s, Input ids: %s", texts, ids)
    return texts, ids


def formats_result(sentiment_output, texts, ids, softmax):
    """Formats model result for output"""

    sentiment_map = {0: "NEGATIVE", 1: "POSITIVE"}
    sentiment_results = []

    for result, text, id in zip(sentiment_output, texts, ids):
        argmax = np.argmax(result)
        softmax_result = softmax(result)
        confidence = {
            "NEGATIVE": float(softmax_result[0]),
            "POSITIVE": float(softmax_result[1]),
        }
        classification = sentiment_map[int(argmax)]
        sentiment_results.append(
            SentimentResult(
                id=id, text=text, confidence=confidence, classification=classification
            )
        )

    logger.debug("Sentence results: %s", sentiment_results)

    return sentiment_results
