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
    reddit_instance = praw.Reddit(
        client_id=client_id,
        client_secret=client_secret,
        user_agent="test_bot"
    )
    # TODO: in authenticate_reddit() add error handling 
    # to failed reddit connections
    print(f'Logged in as user: {reddit_instance.user.me()}')
    return reddit_instance


def get_comments(reddit_instance, url):
    """
    Takes a PRAW reddit instance and a reddit post url
    and returns a list of 5 top level comments.
    """
    
    try:
        submission = reddit_instance.submission(url=url)
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


def connect_sentiment():
    """
    Returns the API url from environment variables.
    """

    sentiment_url = os.getenv("url")
    
    if sentiment_url is None:
        print(f"error: failed to load api url")
        return None
    else:
        return sentiment_url

