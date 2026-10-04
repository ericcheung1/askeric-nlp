import logging
from pathlib import Path

import onnxruntime as ort
from tokenizers import Tokenizer

logger = logging.getLogger(__name__)

DISTILBERT_ONNX = Path("ml/sentiment/distilbert_fp16_onnx/distilbert_fp16.onnx")
TOKENIZER_JSON = Path("ml/sentiment/distilbert_fp16_onnx/tokenizer.json")


def sentiment_load_model():
    """Loads sentiment model in onnx runtime"""

    try:
        sess_options = ort.SessionOptions()

        # Lock ONNX to single-threaded execution to prevent context-switching overhead
        sess_options.intra_op_num_threads = 1
        sess_options.inter_op_num_threads = 1
        sess_options.execution_mode = ort.ExecutionMode.ORT_SEQUENTIAL

        model_session = ort.InferenceSession(
            DISTILBERT_ONNX, providers=["CPUExecutionProvider"]
        )
        logger.info("Successfully Loaded Sentiment Model in 'sentiment_load_model'")

        return model_session

    except Exception as e:
        logger.critical(f"{e!s} in 'sentiment_load_model'")
        raise FileNotFoundError


def sentiment_load_tokenizer():
    """Loads tokenizer"""

    try:
        tokenizer = Tokenizer.from_file(str(TOKENIZER_JSON))
        tokenizer.enable_padding(pad_id=0, pad_token="[PAD]", direction="right")
        logger.info("Successfully Loaded Tokenizer in 'sentiment_load_tokenizer'")

        return tokenizer

    except Exception as e:
        logger.critical(f"{e!s} in 'sentiment_load_tokenizer'")
        raise FileNotFoundError
