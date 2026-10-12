import anyio
from fastapi import APIRouter, Form, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from app.clients.cache import query_from_table, write_to_table
from app.clients.reddit import get_post, parse_submission_id
from app.core.sentiment import score_sentiment
from app.core.webpage_service.common import VERSION, random_url
from app.core.webpage_service.reddit_requests import (
    build_tree,
    calculate_overall_sentiment,
    format_reddit_input,
    format_reddit_output,
    # save_post,
)
from app.core.webpage_service.sentence_requests import (
    clean_sentence_input,
    format_sentence_input,
    format_sentence_output,
)

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")
limiter_1 = anyio.CapacityLimiter(1)
limiter_3 = anyio.CapacityLimiter(3)


@router.get("/", response_class=HTMLResponse)
def index(request: Request):

    urls = request.state.urls
    highlight_post = random_url(urls)

    context = {
        "version": VERSION, 
        # "highlight_post": highlight_post
    }

    return templates.TemplateResponse(
        request=request, name="index.html", 
        context=context
    )


@router.post("/sentence-request", response_class=HTMLResponse)
async def user_input(request: Request, input: str = Form(...)):

    sia = request.state.sia

    clean_sentence_input(input=input)
    text_input = format_sentence_input(input=input)

    output_list = score_sentiment(sia=sia, text_inputs=text_input)

    classification, confidence = format_sentence_output(output_list=output_list)

    context = {
        "classification": classification,
        "confidence": confidence,
    }

    return templates.TemplateResponse(
        request=request, name="sentence_result.html", context=context
    )


@router.post("/reddit-request", response_class=HTMLResponse)
async def reddit_input(request: Request, url: str = Form(...)):

    con = request.state.con
    reddit = request.state.reddit
    sia = request.state.sia

    submission_id = parse_submission_id(url=url)
    # comment_tree, overall_sentiment, post_data = await anyio.to_thread.run_sync(
    #     query_from_table, submission_id, con
    # )
    comment_tree = None
    overall_sentiment = None
    post_data = None

    if comment_tree is None or overall_sentiment is None or post_data is None:
        post_data = await get_post(reddit=reddit, id=submission_id)
        comments = post_data.pop("comments")
        comment_tree, comment_map = build_tree(comments=comments)

        text_inputs = format_reddit_input(comment_map=comment_map)
        
        output_list = score_sentiment(sia=sia, text_inputs=text_inputs)
        
        format_reddit_output(output_list=output_list, comment_map=comment_map)

        overall_sentiment = calculate_overall_sentiment(comment_tree=comment_tree)

        # await anyio.to_thread.run_sync(
        #     write_to_table,
        #     submission_id,
        #     comment_tree,
        #     overall_sentiment,
        #     post_data,
        #     con,
        #     limiter=limiter_3,
        # )

    # save_post(
    #     submission_id=submission_id,
    #     post_data=post_data,
    #     comment_tree=comment_tree,
    #     overall_sentiment=overall_sentiment,
    # )

    context = {
        "comment_tree": comment_tree,
        "overall_sentiment": overall_sentiment,
        "post_title": post_data["title"],
        "post_body": post_data["post_body"],
        "subreddit_name": post_data["subreddit"],
        "post_author": post_data["author"],
    }

    return templates.TemplateResponse(
        request=request, name="reddit_result.html", context=context
    )
