from pathlib import Path
from tokenizers import Tokenizer
import onnxruntime as ort
import numpy as np
import logging

logger = logging.getLogger(__name__)

DISTILBERT_ONNX = Path("ml/sentiment/distilbert_fp16_onnx/distilbert_fp16.onnx")
TOKENIZER_JSON = Path("ml/sentiment/distilbert_fp16_onnx/tokenizer.json")

def sentiment_load_model():
    """Loads sentiment model in onnx runtime"""

    try:
        model_session = ort.InferenceSession(DISTILBERT_ONNX, providers=["CPUExecutionProvider"])
        logger.info("Successfully Loaded Sentiment Model in 'sentiment_load_model'")

        return model_session

    except Exception as e:
        logger.critical(f"{str(e)} in 'sentiment_load_model'")
        raise FileNotFoundError


def sentiment_load_tokenizer():
    """Loads tokenizer"""

    try:
        tokenizer = Tokenizer.from_file(str(TOKENIZER_JSON))
        tokenizer.enable_padding(pad_id=0, pad_token="[PAD]", direction="right")
        logger.info("Successfully Loaded Tokenizer in 'sentiment_load_tokenizer'")

        return tokenizer
    
    except Exception as e:
        logger.critical(f"{str(e)} in 'sentiment_load_tokenizer'")
        raise FileNotFoundError


def sentiment_score(model_session, tokenizer, input):
    """
    Takes a onnx model session, tokenizer from tokenizers library,
    tokenized text input, and text ids. Runs distilbert model on 
    text inputs and returns output logits as a list.
    """

    tokenized_inputs = tokenizer.encode_batch(input)
    token_ids = np.array([item.ids for item in tokenized_inputs])
    attention_masks = np.array([item.attention_mask for item in tokenized_inputs])

    inputs = {
        "input_ids": token_ids,
        "attention_mask": attention_masks
    }

    # runs onnx distilbert on tokenized inputs
    # outputs is a n-dim numpy array
    outputs = model_session.run(None, inputs)
    # outputs[0] is dim with model logits and converts to a list
    output_list = outputs[0].tolist()

    return output_list


def softmax(input, axis=None):
    """An implementation of the softmax function"""

    x = np.array(input)
    e_x = np.exp(x - np.max(x, axis=axis, keepdims=True))
    return e_x / np.sum(e_x, axis=axis, keepdims=True)