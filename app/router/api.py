import anyio
from fastapi import APIRouter, Request

from app.core.api_service import (
    clean_sentence_input,
    formats_result,
    prepare_model_inputs,
    SentenceInput,
    SentenceOutput
)
from app.core.multiprocessing_service import start_inference_process
from ml.sentiment.inference import softmax

router = APIRouter()
limiter_3 = anyio.CapacityLimiter(3)


@router.get("/ping")
async def healthcheck(request: Request):
    return {"message": "service healthy"}


@router.post("/api/v1/sentence-sentiment", response_model=SentenceOutput)
async def sentence_sentiment(request: Request, sentence_input: SentenceInput):

    result_queue = request.state.result_queue
    task_queue = request.state.task_queue
    inference_process = request.state.inference_process

    if not inference_process.is_alive():
        task_queue, result_queue, inference_process = start_inference_process()
        request.state.result_queue = result_queue
        request.state.task_queue = task_queue
        request.state.inference_process = inference_process

    # clean comments, preparing for sentiment scoring
    clean_sentence_input(sentence_input=sentence_input)
    texts, ids = prepare_model_inputs(sentence_input=sentence_input)

    # scores comments with sentiment in separate process
    task_queue.put(texts)
    sentiment_output = result_queue.get()

    sentiment_results = formats_result(
        sentiment_output=sentiment_output,
        texts=texts,
        ids=ids,
        softmax=softmax
    )

    output = SentenceOutput(id=sentence_input.id, sentiment=sentiment_results)

    return output