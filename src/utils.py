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
    and list of at most 15 comments.
    """
    
    try:
        submission = reddit_instance.submission(url=url)
    except InvalidURL:
        return {"error": "invalid url"}
    except RedditAPIException:
        return {"error": "reddit api"}

    # replace_more() method opens "MoreComments" objects
    # limit parameter sets number of "MoreComments" to replace
    submission.comments.replace_more(limit=5)

    # seeds to first 5 top level comments
    comment_stack = submission.comments[:5]
    count = 0
    comments = []
    comment_map = {}

    # DFS traversal of comment forest
    # copies comment tree structure to comments list
    while comment_stack:
        # pops top of stack/last element of list
        comment = comment_stack.pop()
        print(comment)

        comment_info = {
                "comment_id": str(comment.id),
                "user_id": str(comment.author.id),
                "parent_id": str(comment.parent_id),
                "comment": str(comment.body),
                "replies": []
        }

        # maps comment id as key, comment info as value
        # acts as reference to append replies to
        # dicts are pass by reference
        comment_map[comment.id] = comment_info

        # top level comment's parent id starts with t3_
        if comment.parent_id.startswith("t3_"):
            comments.append(comment_info)
            count+=1

        # replies' parent id starts with t1_
        # appends to dict in comment map which also modifies 
        # dict in comment list
        elif comment.parent_id.startswith("t1_"):
            parent_id = comment.parent_id[3:]
            if parent_id in comment_map:
                comment_map[parent_id]["replies"].append(comment_info)
                count+=1
        
        if count >= 15:
            break

        # push replies to top of stack/end of list
        comment_stack.extend(comment.replies)
        
    return comments

def connect_sentiment():
    """
    Returns the API url from environment variables
    """

    sentiment_url = os.getenv("url")
    
    if sentiment_url is None:
        print(f"error: failed to load api url")
        return None
    else:
        return sentiment_url

if __name__ == "__main__":
    from dotenv import load_dotenv
    import json

    load_dotenv()
    reddit = authenticate_reddit()
    url = "https://www.reddit.com/r/nba/comments/1tfb662/vorkunov_dundon_on_not_sending_2way_players_on/"
    
    comments = get_comments(reddit, url)
    print(json.dumps(comments, indent=4))
    with open("data.json", "w") as file:
        json.dump(comments, file, indent=4)
