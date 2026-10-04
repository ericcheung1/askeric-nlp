import numpy as np

from app.core.webpage_service.common import softmax


def clean_sentence_input(input):
    input.strip().lower()


def format_sentence_input(input):
    return [input]


def format_sentence_output(output_list):
    sentiment_map = {0: "NEGATIVE", 1: "POSITIVE"}
    for output in output_list:
        conf = softmax(output)
        argmax = np.argmax(output)
        pred_label = sentiment_map[int(argmax)]

    return pred_label, conf
