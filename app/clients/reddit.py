import copy
import logging
import os
import re

import asyncpraw
from asyncpraw.exceptions import RedditAPIException, InvalidURL
from asyncprawcore.exceptions import NotFound

from app.clients.exceptions import CommentFetchingError

logger = logging.getLogger(__name__)

def start_reddit_client():
    """Authenticates a reddit instance in AsyncPRAW"""

    try:
        reddit = asyncpraw.Reddit(
            client_id=os.getenv("client_id"),
            client_secret=os.getenv("client_secret"),
            user_agent="web:askeric-nlp:v0.0.5 (by u/eric321k)"
        )
        logger.info("Successfully Started Reddit Client in 'start_reddit_client'")

        return reddit

    except Exception as e:
        logger.critical(f"{e} in 'start_reddit_client'")
        raise RuntimeError


def parse_submission_id(url):
    """Parses submission id from url to act as primary key in cache table"""

    pattern = r"^https?:\/\/(?:www\.)?reddit\.com\/r\/\w+\/comments\/([a-z0-9]+)(?:\/[^\s\/]+)?\/?$"
    match = re.fullmatch(pattern, url)

    if match:
        submission_id = match.group(1)
        return submission_id

    else:
        raise CommentFetchingError(message="Failed to Parse For Submission ID")


async def get_comments(reddit, id):
    """
    Takes a AsyncPRAW reddit instance and a reddit post url
    and returns a list of 5 top level comments
    """

    try:
        submission = await reddit.submission(id=id)
        submission_id = submission.id
        submission_title = submission.title
        submission_selftext = submission.selftext
        submission_subreddit = submission.subreddit.display_name
        submission_author = submission.author.name

        # replace_more() method opens "MoreComments" objects
        # limit parameter sets number of "MoreComments" to replace
        await submission.comments.replace_more(limit=5)
        comments = submission.comments[:]

        logger.debug("Comments from from submission [%s] in 'get_comments':\n%s", submission_id, comments)

        if not comments:
            raise CommentFetchingError(message=f"No Comments Found")

        logger.info("Successfully Retrieved Comments in 'get_comments'")

        metadata = {
            "title": submission_title,
            "post_body": submission_selftext,
            "subreddit": submission_subreddit,
            "author": submission_author
        }

        return comments, metadata

    except InvalidURL as e:
        raise CommentFetchingError(message=f"{str(e)}") from e

    except RedditAPIException as e:
        raise CommentFetchingError(message=f"{str(e)}") from e

    except NotFound as e:
        raise CommentFetchingError(message=f"{str(e)}") from e

    except Exception as e:
        raise CommentFetchingError(message=f"{str(e)}") from e


async def close_reddit_client(reddit):
    """Closes connect to AsyncPRAW reddit instance"""
    await reddit.close()


def process_comments(comments):
    """Processes comments into model_inputs map"""

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
            "comment_id": str(comment.id),
            "parent_id": str(comment.parent_id),
            "username": str(comment.author.name) if comment.author else "[user]",
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
