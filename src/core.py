import httpx
import json

def comment_tree(comment_stack):
    """
    Takes a comment_stack object from get_comments() and 
    recreates the comment tree structure through a DFS approach
    and creates payload for wpaas api.
    """
    count = 0
    comments = []
    comment_map = {}
    texts = []

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
                "comment": str(comment.body),
                "replies": []
        }

        # append text id and text body to payload list
        texts.append({
            "text": str(comment.body),
            "text_id": str(comment.id)
        })

        # maps comment id as key, comment info as value
        # acts as a reference to append replies to
        comment_map[comment.id] = comment_info

        # top level comments' parent id starts with t3_
        if comment.parent_id.startswith("t3_"):
            comments.append(comment_info)
            count+=1

        # replies' parent id starts with t1_
        elif comment.parent_id.startswith("t1_"):

            parent_id = comment.parent_id[3:]

            if parent_id in comment_map:

                # this modifies 'replies' field in the 'comments' list
                comment_map[parent_id]["replies"].append(comment_info)
                count+=1
        
        if count >= 15:
            break

        # push replies to top of stack/end of list
        comment_stack.extend(comment.replies)

    payload = {"texts": texts}
        
    return comments, payload


def call_sentiment_endpoint(payload, sentiment_url):
    """
    Takes the formatted payload object and uses it to make 
    a call to the wpaas sentiment endpoint.
    """
    if sentiment_url is None:
        return {"error": "api key cannot be located"}
    
    try:
        response = httpx.post(sentiment_url, json=payload, timeout=60)

        if response.status_code == 404:
            return {"error": "incorrect api url"}
        elif response.status_code != 200:
            return {"error": "http error"}
    except httpx.ConnectError:
        return {"error": "sentiment api connection error"}
    except httpx.TimeoutException:
        return {"error": "timeout error"}
    except httpx.RequestError:
        return {"error": "request error"}
    except Exception as e:
        return {"error": f"{e}"}
    
    return response.json()


def calculate_final_sentiment(comments):
    """
    Takes the response object and calculates average/overall
    sentiment amongst comments in the submitted post.
    """
    count = {"NEGATIVE": 0, "POSITIVE": 0}
    confidence = float(0)

    # same DFS approach to traverse comment tree
    comment_stack = []
    comment_stack.extend(comments[:])

    while comment_stack:
        comment = comment_stack.pop()

        confidence += max(comment["sentiment"]["score"])

        if comment["sentiment"]["classification"] == "NEGATIVE":
            count["NEGATIVE"] += 1
        elif comment["sentiment"]["classification"] == "POSITIVE":
            count["POSITIVE"] += 1
        
        if "replies" in comment:
            comment_stack.extend(comment["replies"])


    mean_conf = confidence/sum(count.values())
    return [{"count": count},
            {"confidence": round(mean_conf, 3)}]


def format_response(comments, response):
    """
    Takes the payload and response objects and builds comment
    tree structure with sentiment analysis results to be rendered 
    in jinja templates
    """
    # comment_id, comment key-value pair e.g {"abc124": "this is the comment"}
    payload_map = {}
    for res in response["sentiment"]:
        payload_map.update({
            res["text_id"]: {
                "classification": res["sentiment_classification"],
                "score": res["sentiment_confidence"],
                "text_id": res["text_id"]
                }
            })
    

    # enriches comment tree with sentiment results via same DFS approach
    comment_stack = []
    comment_stack.extend(comments[:])

    while comment_stack:
        comment = comment_stack.pop()

        comment["sentiment"] = payload_map[comment["comment_id"]]

        if "replies" in comment:
            comment_stack.extend(comment["replies"])

    return comments

