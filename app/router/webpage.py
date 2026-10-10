import anyio
from fastapi import APIRouter, Form, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from app.clients.cache import query_from_table, write_to_table
from app.clients.reddit import (
    get_post,
    parse_submission_id,
)
from app.core.inference_process import start_inference_process
from app.core.webpage_service.common import VERSION
from app.core.webpage_service.reddit_requests import (
    build_tree,
    calculate_overall_sentiment,
    format_reddit_input,
    format_reddit_output,
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
    return templates.TemplateResponse(
        request=request, name="index.html", context={"version": VERSION}
    )


@router.post("/sentence-request", response_class=HTMLResponse)
async def user_input(request: Request, input: str = Form(...)):

    result_queue = request.state.result_queue
    task_queue = request.state.task_queue
    inference_process = request.state.inference_process

    if not inference_process.is_alive():
        task_queue, result_queue, inference_process = start_inference_process()
        request.state.result_queue = result_queue
        request.state.task_queue = task_queue
        request.state.inference_process = inference_process

    clean_sentence_input(input=input)
    text_input = format_sentence_input(input=input)

    # scores comments with sentiment in separate process
    task_queue.put(text_input)
    output_list = result_queue.get()

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
    result_queue = request.state.result_queue
    task_queue = request.state.task_queue
    inference_process = request.state.inference_process

    if not inference_process.is_alive():
        task_queue, result_queue, inference_process = start_inference_process()
        request.state.result_queue = result_queue
        request.state.task_queue = task_queue
        request.state.inference_process = inference_process

    submission_id = parse_submission_id(url=url)
    comment_tree, overall_sentiment, post_data = await anyio.to_thread.run_sync(
        query_from_table, submission_id, con
    )
    print(post_data==True)

    if comment_tree is None or overall_sentiment is None or post_data is None:
        post_data = await get_post(reddit=reddit, id=submission_id)
        comments = post_data.pop("comments")
        comment_tree, comment_map = build_tree(comments=comments)

        text_inputs = format_reddit_input(comment_map=comment_map)

        task_queue.put(text_inputs)
        output_list = result_queue.get()

        format_reddit_output(output_list=output_list, comment_map=comment_map)

        overall_sentiment = calculate_overall_sentiment(comment_tree=comment_tree)

        await anyio.to_thread.run_sync(
            write_to_table,
            submission_id,
            comment_tree,
            overall_sentiment,
            post_data,
            con,
            limiter=limiter_3,
        )

    import json
    info = {
        "submission_id": submission_id,
        "post_data": post_data,
        "comment_tree": comment_tree,
        "overall_sentiment": overall_sentiment,
    }
    with open(f"post-{submission_id}.json", mode="w") as f:
        f.write(json.dumps(info, default=str, indent=2))

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
