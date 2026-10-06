import logging
import multiprocessing
import os

import numpy as np

from ml.sentiment.load import (
    sentiment_load_model,
    sentiment_load_tokenizer,
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
        target=inference_loop, args=(task_queue, result_queue)
    )

    inference_process.start()

    return task_queue, result_queue, inference_process


def score_sentiment(model_session, tokenizer, text_inputs):
    """Sentiment scoring for both request type"""
    tokenized_inputs = tokenizer.encode_batch(text_inputs)
    token_ids = np.array([item.ids for item in tokenized_inputs])
    attention_masks = np.array([item.attention_mask for item in tokenized_inputs])
    inputs = {"input_ids": token_ids, "attention_mask": attention_masks}

    # runs onnx distilbert on tokenized inputs
    # outputs is a n-dim numpy array
    outputs = model_session.run(None, inputs)
    # outputs[0] is dim with model logits and converts to a list
    output_list = outputs[0].tolist()

    return output_list


def inference_loop(task_queue, result_queue):
    """Target function for dedicated inference process"""
    model_session = sentiment_load_model()
    tokenizer = sentiment_load_tokenizer()

    while True:
        job = task_queue.get()

        if job is None:
            break

        text_inputs = job

        output_list = score_sentiment(
            model_session=model_session, tokenizer=tokenizer, text_inputs=text_inputs
        )

        result_queue.put(output_list)
