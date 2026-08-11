import praw
from praw.exceptions import RedditAPIException, InvalidURL
import os
import logging
import copy

logger = logging.getLogger(__name__)

def start_reddit_client():
    """Authenticates a reddit instance in PRAW"""

    try:
        reddit = praw.Reddit(
            client_id=os.getenv("client_id"),
            client_secret=os.getenv("client_secret"),
            user_agent="test_bot"
        )
        logger.info("Successfully Started Reddit Client in 'start_reddit_client'")

    except Exception as e:
        logger.critical(f"Exception {e}: Failed to Start Reddit Client in 'start_reddit_client'")
        raise ValueError

    # TODO: in authenticate_reddit() add error handling 
    # to failed reddit connections

    return reddit


def get_comments(reddit, url):
    """
    Takes a PRAW reddit instance and a reddit post url
    and returns a list of 5 top level comments.
    """
    # NOTE: log the errors then figure out how to handle downstream effects
    try:
        submission = reddit.submission(url=url)

    except InvalidURL:
        logger.warning("Invalid URL Error Encountered in 'get_comments'")
        return {"error": "invalid url"}

    except RedditAPIException:
        logger.warning("Reddit API Error Encountered in 'get_comments'")
        return {"error": "reddit api"}

    except Exception as e:
        logger.warning("Error Encountered in 'get_comments'")
        return {"error": f"{e}"}

    # replace_more() method opens "MoreComments" objects
    # limit parameter sets number of "MoreComments" to replace
    submission.comments.replace_more(limit=5)
    comments = submission.comments[:5]

    logger.debug("Comments from 'get_comments':\n%s", comments)

    if not comments:
        logger.warning("Failed to Retrieve Comments in 'get_comments'")
        return {"error": "no comments"}

    logger.info("Successfully Retrieved Comments in 'get_comments'")

    return comments


def process_comments(comments):
    """Processes comment_stack into model_inputs map"""

    count = 0
    model_inputs = []

    comment_stack = copy.deepcopy(comments)

    while comment_stack:

        # pops top of stack/last element of list
        comment = comment_stack.pop()

        model_inputs.append({
                "text": str(comment.body),
                "text_id": str(comment.id)
        })
        count+=1

        if count >= 15:
            break

        comment_stack.extend(comment.replies)

    logger.debug("Model Inputs from 'process_comments':\n%s", model_inputs)
    logger.info("Successfully Processed Comments in 'process_comments'")

    return model_inputs


def build_tree(comments):
    """
    Takes a comment_stack object from get_comments() and 
    recreates the comment tree structure through a DFS approach.
    """

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
            "comment_id": str(comment.id),
            "user_id": str(comment.author.id),
            "parent_id": str(comment.parent_id),
            "replies": []
        }

        # maps comment id as key, comment info as value
        # acts as a reference to append replies to
        comment_map[comment.id] = comment_info

        # top level comments' parent id starts with t3_
        if comment.parent_id.startswith("t3_"):
            comment_tree.append(comment_info)
            count+=1

        # replies' parent id starts with t1_
        elif comment.parent_id.startswith("t1_"):

            parent_id = comment.parent_id[3:]

            if parent_id in comment_map:

                # a child's parent id is the parent's comment id
                # this modifies 'replies' field in the 'comments' list
                comment_map[parent_id]["replies"].append(comment_info)
                count+=1
        
        if count >= 15:
            break

        # push replies to top of stack/end of list
        comment_stack.extend(comment.replies)

    logger.debug("Comment Tree from 'build_tree'\n%s", comment_tree)
    logger.info("Successfully Built Comment Tree in 'built_tree'")
        
    return comment_tree
