import httpx

def comment_tree(comment_stack):
    """
    Takes a comment_stack object from get_comments() and 
    recreates the comment tree structure through a DFS approach
    and also creates payload for wpaas api.
    """
    count = 0
    comments = []
    comment_map = {}
    texts = []

    # DFS traversal of comment forest
    # copies comment tree structure to comments list
    # also creates payload in same DFS order
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

        texts.append({
            "text": str(comment.body),
            "text_id": str(comment.id)
        })

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
        print(response)
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


def calculate_final_sentiment(response_json):
    """
    Takes the response object and calculates average/overall
    sentiment amongst comments in the submitted post.
    """
    sentiment_count = {"NEGATIVE": 0, "POSITIVE": 0}
    sentiment_confidence = float(0)

    for result in response_json:

        sentiment_confidence+=max(result["sentiment_confidence"])

        if result["sentiment_classification"] == "NEGATIVE":
            sentiment_count["NEGATIVE"]+=1
        else:
            sentiment_count["POSITIVE"]+=1

    mean_conf = sentiment_confidence/len(response_json)
    return [{"sentiment_count": sentiment_count},
            {"sentiment_confidence": round(mean_conf, 3)}]


def format_response(comments, response):
    """
    Takes the payload and response objects and build one
    context JSON object to be rendered in jinja templates
    """
    # comment_id, comment key-value pair e.g {"abc124": "this is the comment"}
    payload_map = {}
    for res in response["sentiment"]:
        payload_map.update({
            res["text_id"]: {
                "sentiment": res["sentiment_classification"],
                "score": res["sentiment_confidence"],
                "text_id": res["text_id"]
                }
            })
    
    print(f"payload_map: {payload_map}")
    # # appends original text to sentiment result object
    comment_stack = []
    # print(comment_stack)
    comment_stack.append(comments[0])
    # print(comment_stack[0]["parent_id"])

    while comment_stack:
        comment = comment_stack.pop()

        comment["sentiment"] = payload_map[comment["comment_id"]]

        if "replies" in comment:
            comment_stack.extend(comment["replies"])

    # print(f"comments: {comments}")
    # print(json.dumps(comments, indent=4))
    return comments

