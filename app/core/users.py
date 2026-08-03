# from app.schemas.input import UserInputs
import numpy as np

def clean_model_inputs(model_inputs):
    """Lowercase and strip texts"""

    for input in model_inputs:
        text = input.get("text", "")
        cleaned_text = text.lower().strip()
        id = input.get("text_id", "")

        input.update({
            "cleaned_text": cleaned_text
        })


def prepare_model_inputs(model_inputs):
    "Splits inputs into list of strings and list of ids"

    raw_inputs = []
    ids = []
    
    for input in model_inputs:
        raw_inputs.append(input.get("cleaned_text", ""))
        ids.append(input.get("text_id", ""))

    return raw_inputs, ids


def reconcile_outputs(raw_outputs, ids, softmax):

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

    return result_map


def rebuild_comment_tree(comment_tree, result_map):
    """Turns map into tree structure after sentiment scoring"""

    # create and re-seed stack with comments from tree
    comment_stack = []
    comment_stack.extend(comment_tree[:])

    while comment_stack:

        comment = comment_stack.pop()

        # maps all values of result_map into comment_tree via reference
        comment["sentiment"] = result_map[comment["comment_id"]]

        if "replies" in comment:
            comment_stack.extend(comment["replies"])


if __name__ == "__main__":
    model_input = {
        "abc124": {
            "text": "i hate NACHOS  ",
            "text_id": "abc124"
        }
    }
    print("before", model_input)
    clean_model_inputs(model_inputs=model_input)
    print("after", model_input)