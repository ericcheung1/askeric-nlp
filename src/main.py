from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
import uvicorn
from dotenv import load_dotenv
from core import comment_tree, call_sentiment_endpoint, calculate_final_sentiment, format_response
from utils import authenticate_reddit, get_comments, connect_sentiment


app = FastAPI(docs_url=None, redoc_url=None)


load_dotenv()
reddit = authenticate_reddit()
sentiment_endpoint = connect_sentiment()
templates = Jinja2Templates(directory="templates")


@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="index.html"
    )


@app.post("/sentiment-stand-alone", response_class=HTMLResponse)
def sentiment_stand_alone(request: Request, text: str = Form(...)):

    payload = {"texts": [{"text": text}]}
    response = call_sentiment_endpoint(payload, sentiment_endpoint)
    if isinstance(response, dict) and ("error" in response):
        return HTMLResponse(content=f"<div>Could Not Connect to API</div>") 
    
    context = {"response": response}
    
    return templates.TemplateResponse(
        request=request,
        name="result_update_s.html",
        context=context
    )


@app.post("/sentiment-reddit", response_class=HTMLResponse)
def sentiment_reddit(request: Request, url: str = Form(...)):
    
    comment_stack = get_comments(reddit, url)
    if isinstance(comment_stack, dict) and "error" in comment_stack:
        error = comment_stack
        return HTMLResponse(content=f"<div>Result: {error} </div>")
    
    else:
        comments, payload = comment_tree(comment_stack)

        response = call_sentiment_endpoint(payload, sentiment_endpoint)
        if isinstance(response, dict) & ("error" in response):
            error = response
            return HTMLResponse(content=f"<div>Result: {error} </div>")

        formatted_response = format_response(comments, response)
        overall_sentiment = calculate_final_sentiment(comments)
    
    context = {"response": formatted_response, 
                "overall_sentiment": overall_sentiment}
    
    return templates.TemplateResponse(
        request=request,
        name="result_update_r.html",
        context=context
    )


if __name__ == "__main__":
    uvicorn.run("main:app", port=5000, reload=True)