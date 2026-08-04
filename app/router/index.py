from fastapi import APIRouter, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from app.clients.reddit import get_comments, process_comments, build_tree
from app.core.users import (
    clean_model_inputs, 
    prepare_model_inputs, 
    reconcile_outputs, 
    rebuild_comment_tree, 
    calculate_overall_sentiment
)
from ml.sentiment.inference import sentiment_score, softmax


router = APIRouter()

templates = Jinja2Templates(directory="app/templates")

@router.get("/", response_class=HTMLResponse)
def index(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="index.html"
    )


@router.post("/user_input", response_class=HTMLResponse)
def user_input(request: Request, input: str=Form(...)):

    model_session = request.app.state.model_session
    tokenizer = request.app.state.tokenizer

    # build a mock model input object with mock id
    mock_id = "abc123"
    model_inputs = [{
        "text": str(input),
        "text_id": "abc123"
    }]

    # clean comments, preparing for sentiment scoring
    clean_model_inputs(model_inputs=model_inputs)
    raw_inputs, ids = prepare_model_inputs(model_inputs=model_inputs)

    # scores comments with sentiment, formats outputs
    raw_outputs = sentiment_score(model_session=model_session, tokenizer=tokenizer, input=raw_inputs)
    result_map = reconcile_outputs(raw_outputs=raw_outputs, ids=ids, softmax=softmax)

    context = {
        "classification": result_map[mock_id]["sentiment_class"],
        "confidence": result_map[mock_id]["sentiment_conf"]
    }

    return templates.TemplateResponse(
        request=request,
        name="result_update_s.html",
        context=context
    )


@router.post("/reddit_input", response_class=HTMLResponse)
def reddit_input(request: Request, url: str=Form(...)):

    reddit = request.app.state.reddit
    model_session = request.app.state.model_session
    tokenizer = request.app.state.tokenizer

    comments = get_comments(reddit=reddit, url=url)

    # clean comments, preparing for sentiment scoring
    model_inputs = process_comments(comments=comments)
    clean_model_inputs(model_inputs=model_inputs)
    raw_inputs, ids = prepare_model_inputs(model_inputs=model_inputs)

    # pre-building comment tree structure, fill with sentiment scores after
    comment_tree = build_tree(comments=comments)

    # scores comments with sentiment, formats outputs
    raw_outputs = sentiment_score(model_session=model_session, tokenizer=tokenizer, input=raw_inputs)
    result_map = reconcile_outputs(raw_outputs=raw_outputs, ids=ids, softmax=softmax)

    # fills pre-built comment tree with sentiment scores
    rebuild_comment_tree(comment_tree=comment_tree, result_map=result_map)

    overall_sentiment = calculate_overall_sentiment(comment_tree=comment_tree)

    # context object to use in HTML template
    context = {
        "comment_tree": comment_tree,
        "overall_sentiment": overall_sentiment
    }

    return templates.TemplateResponse(
        request=request,
        name="result_update_r.html",
        context=context
    )

    