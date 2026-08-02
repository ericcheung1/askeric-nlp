import praw
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