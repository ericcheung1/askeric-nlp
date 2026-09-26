import anyio
from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse

from app.core.api_service import (
    clean_sentence_input,
    formats_result,
    prepare_model_inputs,
    SentenceInput,
    SetenceOutput,
    SentimentResult
)
from ml.sentiment.inference import sentiment_score, softmax

router = APIRouter()
limiter_1 = anyio.CapacityLimiter(1)
limiter_3 = anyio.CapacityLimiter(3)


@router.get("/ping", response_class=JSONResponse)
async def healthcheck(request: Request):
    return {"message": "service healthy"}


@router.post("/api/v1/sentence-sentiment")
async def sentence_sentiment(request: Request, sentence_input: SentenceInput):

    model_session = request.state.model_session
    tokenizer = request.state.tokenizer

    # clean comments, preparing for sentiment scoring
    clean_sentence_input(sentence_input=sentence_input)
    sentiment_input, id = prepare_model_inputs(sentence_input=sentence_input)

    # scores comments with sentiment, formats outputs
    sentiment_output = await anyio.to_thread.run_sync(
        sentiment_score,
        model_session,
        tokenizer,
        sentiment_input,
        limiter=limiter_3
    )
    classification, confidence = formats_result(
        sentiment_output=sentiment_output,
        softmax=softmax
    )

    sentiment_result = SentimentResult(classification=classification, confidence=confidence)
    output = SetenceOutput(id=id, text=sentence_input.text, sentiment=sentiment_result)

    return output