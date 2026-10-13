import anyio
from fastapi import APIRouter, Request

from app.core.api_service import (
    SentenceInput,
    SentenceOutput,
    clean_sentence_input,
    formats_result,
    prepare_model_inputs,
)
from app.core.sentiment import score_sentiment

router = APIRouter()
limiter_10 = anyio.CapacityLimiter(10)


@router.get("/ping")
async def healthcheck(request: Request):
    return {"message": "service healthy"}


@router.post("/api/v1/sentence-sentiment", response_model=SentenceOutput)
async def sentence_sentiment(request: Request, sentence_input: SentenceInput):

    sia = request.state.sia

    # clean comments, preparing for sentiment scoring
    clean_sentence_input(sentence_input=sentence_input)
    texts, ids = prepare_model_inputs(sentence_input=sentence_input)

    sentiment_output = await anyio.to_thread.run_sync(score_sentiment, sia, texts, limiter=limiter_10)

    sentiment_results = formats_result(
        sentiment_output=sentiment_output, texts=texts, ids=ids
    )

    output = SentenceOutput(id=sentence_input.id, sentiment=sentiment_results)

    return output
