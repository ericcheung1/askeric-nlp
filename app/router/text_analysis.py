import anyio
from fastapi import APIRouter, Form, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from app.clients.reddit import build_tree, get_comments, parse_submission_id, process_comments
from app.clients.cache import query_from_table, write_to_table
from app.core.users import (
    calculate_overall_sentiment,
    clean_model_inputs,
    prepare_model_inputs,
    rebuild_comment_tree,
    reconcile_outputs
)
from ml.sentiment.inference import sentiment_score, softmax

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")
limiter_1 = anyio.CapacityLimiter(1)
limiter_3 = anyio.CapacityLimiter(3)

@router.get("/", response_class=HTMLResponse)
def index(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="index.html"
    )


@router.post("/sentence_input", response_class=HTMLResponse)
async def user_input(request: Request, input: str=Form(...)):

    model_session = request.state.model_session
    tokenizer = request.state.tokenizer

    # build a mock model input object with mock id
    mock_id = "abc123"
    model_inputs = [{
        "text": str(input),
        "text_id": mock_id
    }]

    # clean comments, preparing for sentiment scoring
    clean_model_inputs(model_inputs=model_inputs)
    raw_inputs, ids = prepare_model_inputs(model_inputs=model_inputs)

    # scores comments with sentiment, formats outputs
    raw_outputs = await anyio.to_thread.run_sync(
        sentiment_score,
        model_session,
        tokenizer,
        raw_inputs,
        limiter=limiter_3
    )
    result_map = reconcile_outputs(raw_outputs=raw_outputs, ids=ids, softmax=softmax)

    context = {
        "classification": result_map[mock_id]["sentiment_class"],
        "confidence": result_map[mock_id]["sentiment_conf"]
    }

    return templates.TemplateResponse(
        request=request,
        name="sentence_result.html",
        context=context
    )


@router.post("/reddit_input", response_class=HTMLResponse)
async def reddit_input(request: Request, url: str=Form(...)):

    con = request.state.con
    model_session = request.state.model_session
    reddit = request.state.reddit
    tokenizer = request.state.tokenizer

    submission_id = parse_submission_id(url=url)
    comment_tree, overall_sentiment = await anyio.to_thread.run_sync(
        query_from_table, 
        submission_id, 
        con
    )

    if comment_tree is None and overall_sentiment is None:

        metadata = await get_comments(reddit=reddit, id=submission_id)
        model_inputs = process_comments(comments=metadata["comments"])
        clean_model_inputs(model_inputs=model_inputs)
        raw_inputs, ids = prepare_model_inputs(model_inputs=model_inputs)

        # pre-building comment tree structure, fill with sentiment scores after
        comment_tree = build_tree(comments=metadata["comments"])

        # scores comments with sentiment, formats outputs
        raw_outputs = await anyio.to_thread.run_sync(
            sentiment_score,
            model_session,
            tokenizer,
            raw_inputs,
            limiter=limiter_1
        )
        result_map = reconcile_outputs(raw_outputs=raw_outputs, ids=ids, softmax=softmax)

        # fills pre-built comment tree with sentiment scores
        rebuild_comment_tree(comment_tree=comment_tree, result_map=result_map)
        overall_sentiment = calculate_overall_sentiment(comment_tree=comment_tree)

        await anyio.to_thread.run_sync(
            write_to_table,
            submission_id,
            comment_tree,
            overall_sentiment,
            con,
            limiter=limiter_3
        )

    context = {
        "comment_tree": comment_tree,
        "overall_sentiment": overall_sentiment,
        "post_title": metadata["title"],
        "post_body": metadata["post_body"],
        "subreddit_name": metadata["subreddit"],
        "post_author": metadata["author"]
    }

    return templates.TemplateResponse(
        request=request,
        name="reddit_result.html",
        context=context
    )
