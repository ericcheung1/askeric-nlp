import praw
from praw.exceptions import RedditAPIException, InvalidURL

import os

def authenticate_reddit():
    """
    Authenticates a reddit instance in PRAW.

    Authenticates a reddit instance using 
    information and keys from a .env file.
    """
    client_id = os.getenv("client_id")
    client_secret = os.getenv("client_secret")
    reddit = praw.Reddit(
        client_id=client_id,
        client_secret=client_secret,
        user_agent="test_bot"
    )

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
        return {"error": "invalid url"}
    except RedditAPIException:
        return {"error": "reddit api"}
    except Exception as e:
        return {"error": f"{e}"}

    # replace_more() method opens "MoreComments" objects
    # limit parameter sets number of "MoreComments" to replace
    submission.comments.replace_more(limit=5)
    comment_stack = submission.comments[:5]

    if not comment_stack:
        return {"error": "no comments"}

    return comment_stack


def process_comments(comment_stack):
    """Processes comment_stack into model_inputs map"""
    count = 0
    model_inputs = []

    while comment_stack:

        # pops top of stack/last element of list
        comment = comment_stack.pop()

        model_inputs.append({
                "text": str(comment.body),
                "text_id": str(comment.id),
                "user_id": str(comment.author.id),
                "parent_id": str(comment.parent_id),
                "replies": []
        })
        count+=1

        if count >= 15:
            break

        comment_stack.extend(comment.replies)

    return model_inputs


def build_tree(comment_stack):
    """
    Takes a comment_stack object from get_comments() and 
    recreates the comment tree structure through a DFS approach.
    """
    count = 0
    comment_tree = []
    comment_map = {}

    # DFS traversal of comment forest
    # copies comment tree structure to 'comments' list
    # also creates payload in same DFS order
    while comment_stack:
        # pops top of stack/last element of list
        comment = comment_stack.pop()

        comment_info = {
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
        
    return comment_tree