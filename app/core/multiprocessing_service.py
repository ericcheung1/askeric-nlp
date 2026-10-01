import logging
import multiprocessing
import os

from ml.sentiment.inference import (
    sentiment_load_model,
    sentiment_load_tokenizer,
    sentiment_score
)

DEBUG_LOGS = os.environ.get("DEBUG_LOGS", "0") == "1"

level = logging.DEBUG if DEBUG_LOGS else logging.INFO
logging.basicConfig(
    level=level,
    format="%(asctime)s [PID:%(process)d] [%(levelname)s] %(name)s: %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger(__name__)

def start_inference_process():
    """Starts separate process for ML inference"""
    task_queue = multiprocessing.Queue()
    result_queue = multiprocessing.Queue()

    inference_process = multiprocessing.Process(
        target=inference_loop,
        args=(task_queue, result_queue)
    )

    inference_process.start()

    return task_queue, result_queue, inference_process


def inference_loop(task_queue, result_queue):
    """Inference process target function"""
    model_session = sentiment_load_model()
    tokenizer = sentiment_load_tokenizer() 

    while True:

        job = task_queue.get()

        if job is None:
            break

        raw_inputs = job

        raw_outputs = sentiment_score(
            model_session=model_session,
            tokenizer=tokenizer,
            input=raw_inputs
        )

        logger.info("Processed Input in 'inference_loop'")
        result_queue.put(raw_outputs)