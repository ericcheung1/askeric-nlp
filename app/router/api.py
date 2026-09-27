import anyio
from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse

from app.core.api_service import (
    clean_sentence_input,
    formats_result,
    prepare_model_inputs,
    SentenceInput,
    SentenceOutput
)
from ml.sentiment.inference import sentiment_score, softmax

router = APIRouter()
limiter_3 = anyio.CapacityLimiter(3)


@router.get("/ping")
async def healthcheck(request: Request):
    return {"message": "service healthy"}


@router.post("/api/v1/sentence-sentiment", response_model=SentenceOutput)
async def sentence_sentiment(request: Request, sentence_input: SentenceInput):

    model_session = request.state.model_session
    tokenizer = request.state.tokenizer

    # clean comments, preparing for sentiment scoring
    clean_sentence_input(sentence_input=sentence_input)
    texts, ids = prepare_model_inputs(sentence_input=sentence_input)

    # scores comments with sentiment, formats outputs
    sentiment_output = await anyio.to_thread.run_sync(
        sentiment_score,
        model_session,
        tokenizer,
        texts,
        limiter=limiter_3
    )
    sentiment_results = formats_result(
        sentiment_output=sentiment_output,
        texts=texts,
        ids=ids,
        softmax=softmax
    )

    output = SentenceOutput(id=sentence_input.id, sentiment=sentiment_results)

    return output