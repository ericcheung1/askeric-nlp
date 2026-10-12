# import numpy as np

# from app.core.webpage_service.common import softmax


def clean_sentence_input(input):
    """Cleans input for sentence request type"""
    input.strip()


def format_sentence_input(input):
    """Formats input for sentence request type"""
    return [input]


def _format_sentence_output(output_list):
    """Formats sentiment label and confidence output for sentence request type"""
    # sentiment_map = {0: "NEGATIVE", 1: "POSITIVE"}
    # for output in output_list:
    #     conf = softmax(output)
    #     argmax = np.argmax(output)
    #     pred_label = sentiment_map[int(argmax)]

    # return pred_label, conf


def format_sentence_output(output_list):
    """Formats sentiment label and confidence output for sentence request type"""
    for output in output_list:
        if output >= 0.05:
            label = "POSITIVE"
        elif output <= -0.05:
            label = "NEGATIVE"
        else:
            label = "NEUTRAL"

    return label, [output]