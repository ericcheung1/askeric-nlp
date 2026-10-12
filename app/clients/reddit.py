import logging
import os
import re

import asyncpraw
from asyncpraw.exceptions import InvalidURL, RedditAPIException
from asyncprawcore.exceptions import NotFound

from app.clients.exceptions import CommentFetchingError

logger = logging.getLogger(__name__)


def start_reddit_client():
    """Authenticates a reddit instance in AsyncPRAW"""

    try:
        reddit = asyncpraw.Reddit(
            client_id=os.getenv("CLIENT_ID"),
            client_secret=os.getenv("CLIENT_SECRET"),
            user_agent="web:askeric-nlp (by u/eric321k)",
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


async def get_post(reddit, id):
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
        submission_url = submission.url

        # replace_more() method opens "MoreComments" objects
        # limit parameter sets number of "MoreComments" to replace
        await submission.comments.replace_more(limit=5)
        comments = submission.comments[:]

        logger.debug(
            "Comments from from submission [%s] in 'get_post':\n%s",
            submission_id,
            comments,
        )

        if not comments:
            raise CommentFetchingError(message="No Comments Found")

        logger.info("Successfully Retrieved Comments in 'get_post'")

        post = {
            "comments": comments,
            "title": submission_title,
            "post_body": submission_selftext,
            "subreddit": submission_subreddit,
            "author": submission_author,
            "url": submission_url,
        }

        return post

    except InvalidURL as e:
        raise CommentFetchingError(message=f"{e!s}") from e

    except RedditAPIException as e:
        raise CommentFetchingError(message=f"{e!s}") from e

    except NotFound as e:
        raise CommentFetchingError(message=f"{e!s}") from e

    except Exception as e:
        raise CommentFetchingError(message=f"{e!s}") from e


async def close_reddit_client(reddit):
    """Closes connect to AsyncPRAW reddit instance"""
    await reddit.close()
