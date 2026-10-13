import logging

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
    score: float


class SentenceOutput(BaseModel):
    """Represents an outgoing output payload with list of results"""

    id: str | None = None
    sentiment: list[SentimentResult]


def clean_sentence_input(sentence_input: SentenceInput):
    """Lowercase and strip text in sentence input"""
    for item in sentence_input.inputs:
        item.text = item.text.strip()

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


def formats_result(sentiment_output, texts, ids):
    """Formats model result for output"""

    sentiment_results = []

    for score, text, id in zip(sentiment_output, texts, ids):
        if score >= 0.05:
            classification = "POSITIVE"
        elif score <= -0.05:
            classification = "NEGATIVE"
        else:
            classification = "NEUTRAL"

        sentiment_results.append(
            SentimentResult(
                id=id, text=text, score=score, classification=classification
            )
        )

    logger.debug("Sentence results: %s", sentiment_results)

    return sentiment_results
