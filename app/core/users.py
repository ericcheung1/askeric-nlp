import numpy as np
import logging
import json
import copy

logger = logging.getLogger(__name__)

def clean_model_inputs(model_inputs):
    """Lowercase and strip texts"""

    for input in model_inputs:
        text = input.get("text", "")
        cleaned_text = text.lower().strip()
        id = input.get("text_id", "")

        input.update({
            "cleaned_text": cleaned_text
        })

    logger.debug("Cleaned Model Inputs from 'clean_model_inputs':\n%s", model_inputs)
    logger.info("Successfully Cleaned Model Inputs in 'clean_model_inputs'")


def prepare_model_inputs(model_inputs):
    """Splits inputs into list of strings and list of ids"""

    raw_inputs = []
    ids = []
    
    for input in model_inputs:
        raw_inputs.append(input.get("cleaned_text", ""))
        ids.append(input.get("text_id", ""))

    return raw_inputs, ids


def reconcile_outputs(raw_outputs, ids, softmax):
    """Zips sentiment scores back with their respective comment ids"""

    sentiment_map = {0: "NEGATIVE", 1: "POSITIVE"}
    result_map = {}

    for result, id in zip(raw_outputs, ids):
        conf = softmax(result)
        argmax = np.argmax(result)
        pred_label = sentiment_map[int(argmax)]

        result_map.update({
            id: {
                "sentiment_class": pred_label,
                "sentiment_conf": conf.tolist()
            }
        })

    logger.debug("Result Map from 'reconcile_outputs'\n%s", result_map)
    logger.info("Successfully Reconciled Sentiment Scores with Comment IDs in 'reconcile_outputs'")

    return result_map


def rebuild_comment_tree(comment_tree, result_map):
    """Add sentiment scores back into tree structure"""

    # create and re-seed stack with comments from tree
    comment_stack = []
    comment_stack.extend(comment_tree[:])

    while comment_stack:

        comment = comment_stack.pop()

        # maps all values of result_map into comment_tree via reference
        comment["sentiment"] = result_map[comment["comment_id"]]

        if "replies" in comment:
            comment_stack.extend(comment["replies"])

    pretty_comment_tree = json.dumps(comment_tree, default=str, indent=4)
    logger.debug("Final Comment Tree from 'rebuild_comment_tree'\n%s", pretty_comment_tree)
    logger.info("Successfully Rebuilt Comment Tree with Sentiment Scores in 'rebuild_comment_tree'")


def calculate_overall_sentiment(comment_tree):

    count = {"Negative": 0, "Positive": 0}
    total_conf = float(0)

    comment_tree_copy = copy.deepcopy(comment_tree)
    comment_stack = []
    comment_stack.extend(comment_tree_copy[:])

    while comment_stack:

        comment = comment_stack.pop()

        total_conf += max(comment["sentiment"]["sentiment_conf"])

        if comment["sentiment"]["sentiment_class"] == "NEGATIVE":
            count["Negative"] += 1
        elif comment["sentiment"]["sentiment_class"] == "POSITIVE":
            count["Positive"] += 1


        if "replies" in comment:
            comment_stack.extend(comment["replies"])


    avg_conf = total_conf / sum(count.values())

    logger.info("Successfully Calculated Overall Sentiment in 'calculate_overall_sentiment'")

    return [{
        "count": count,
        "confidence": round(avg_conf, 3)
    }]


if __name__ == "__main__":
    pass