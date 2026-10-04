import copy
import json
import logging

import numpy as np

from app.core.webpage_service.common import softmax

logger = logging.getLogger(__name__)
MAX_COMMENTS = 15


def build_tree(comments):
    """Takes comments and recreates the comment tree structure through a DFS approach"""

    count = 0
    comment_tree = []
    comment_map = {}
    comment_stack = copy.deepcopy(comments)

    # DFS traversal of comment forest
    # copies comment tree structure to 'comments' list
    # also creates payload in same DFS order
    while comment_stack:
        # pops top of stack/last element of list
        comment = comment_stack.pop()

        comment_info = {
            "comment": str(comment.body),
            "cleaned_comment": str(comment.body).strip().lower(),
            "comment_id": str(comment.id),
            "parent_id": str(comment.parent_id),
            "username": str(comment.author.name) if comment.author else "[user]",
            "replies": [],
        }

        # maps comment id as key, comment info as value
        # acts as a reference to append replies to
        comment_map[comment.id] = comment_info

        # top level comments' parent id starts with t3_
        if comment.parent_id.startswith("t3_"):
            comment_tree.append(comment_info)
            count += 1

        # replies' parent id starts with t1_
        elif comment.parent_id.startswith("t1_"):
            parent_id = comment.parent_id[3:]

            if parent_id in comment_map:
                # a child's parent id is the parent's comment id
                # this modifies 'replies' field in the 'comments' list
                comment_map[parent_id]["replies"].append(comment_info)
                count += 1

        if count >= MAX_COMMENTS:
            break

        # push replies to top of stack/end of list
        comment_stack.extend(comment.replies)

    logger.debug(
        "Comment Tree from 'build_tree'\n%s",
        json.dumps(comment_tree, default=str, indent=2),
    )
    logger.info("Successfully Built Comment Tree in 'built_tree'")

    return comment_tree, comment_map


def format_reddit_input(comment_map):
    """Formats inputs for Reddit request type"""
    text_inputs = []
    for comment_info in comment_map.values():
        text_inputs.append(comment_info.get("cleaned_comment", ""))

    return text_inputs


def format_reddit_output(output_list, comment_map):
    """Formats outputs for Reddit request type"""
    sentiment_map = {0: "NEGATIVE", 1: "POSITIVE"}

    for output, comment_info in zip(output_list, comment_map.values()):
        conf = softmax(output)
        argmax = np.argmax(output)
        pred_label = sentiment_map[int(argmax)]

        comment_info["sentiment_class"] = pred_label
        comment_info["sentiment_conf"] = conf.tolist()


def calculate_overall_sentiment(comment_tree):
    """Calculates counts and averages for sentiment in comment tree"""

    count = {"Negative": 0, "Positive": 0}
    total_conf = float(0)

    comment_tree_copy = copy.deepcopy(comment_tree)
    comment_stack = []
    comment_stack.extend(comment_tree_copy[:])

    while comment_stack:
        comment = comment_stack.pop()

        total_conf += max(comment["sentiment_conf"])

        if comment["sentiment_class"] == "NEGATIVE":
            count["Negative"] += 1
        elif comment["sentiment_class"] == "POSITIVE":
            count["Positive"] += 1

        if "replies" in comment:
            comment_stack.extend(comment["replies"])

    try:
        avg_conf = total_conf / sum(count.values())
    except ZeroDivisionError:
        avg_conf = 0

    logger.info(
        "Successfully Calculated Overall Sentiment in 'calculate_overall_sentiment'"
    )

    return {"count": count, "confidence": round(avg_conf, 3)}
