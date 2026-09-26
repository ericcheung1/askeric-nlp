import logging
import numpy as np
from typing import List
from pydantic import BaseModel

logger = logging.getLogger(__name__)

class SentenceInput(BaseModel):
    id: str | None = "abc123"
    text: str


class SentimentResult(BaseModel):
    classification: str
    confidence: List


class SetenceOutput(BaseModel):
    id: str | None = "abc123"
    text: str
    sentiment: SentimentResult


def clean_sentence_input(sentence_input: SentenceInput):
    """Lowercase and strip text in sentence input"""
    sentence_input.text = sentence_input.text.lower().strip()

    logger.debug("Cleaned input: %s", sentence_input.text)


def prepare_model_inputs(sentence_input: SentenceInput):
    """Splits inputs into text and id"""

    logger.debug("Input text: %s, Input id: %s", sentence_input.text, sentence_input.id)
    return list(sentence_input.text), sentence_input.id


def formats_result(sentiment_output, softmax):
    """Formats model result for outut"""

    sentiment_map = {0: "NEGATIVE", 1: "POSITIVE"}

    argmax = np.argmax(sentiment_output[0])
    confidence = softmax(sentiment_output[0])
    classification = sentiment_map[int(argmax)]

    return classification, confidence