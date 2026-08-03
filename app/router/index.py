from fastapi import APIRouter, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from app.clients.reddit import get_comments, process_comments, build_tree
from app.core.users import clean_model_inputs, prepare_model_inputs, reconcile_outputs, rebuild_comment_tree
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
    pass


@router.post("/reddit_input", response_class=HTMLResponse)
def reddit_input(request: Request, url: str=Form(...)):

    reddit = request.app.state.reddit
    if reddit:
        print("reddit loaded")
    model_session = request.app.state.model_session
    if model_session:
        print("model loaded")
    tokenizer = request.app.state.tokenizer
    if tokenizer:
        print("tokenizer loaded")

    comment_stack = get_comments(reddit=reddit, url=url)
    model_inputs = process_comments(comment_stack=comment_stack)
    comment_tree = build_tree(comment_stack=comment_stack)

    clean_model_inputs(model_inputs=model_inputs)
    raw_inputs, ids = prepare_model_inputs(model_inputs=model_inputs)

    raw_outputs = sentiment_score(model_session=model_session, tokenizer=tokenizer, input=raw_inputs)
    result_map = reconcile_outputs(raw_outputs=raw_outputs, ids=ids, softmax=softmax)
    rebuild_comment_tree(comment_tree=comment_tree, result_map=result_map)

    print(comment_tree)

    