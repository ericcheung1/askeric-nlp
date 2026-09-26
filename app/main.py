import logging
import os

from contextlib import asynccontextmanager
from dotenv import load_dotenv
from fastapi import FastAPI
import uvicorn

from app.clients.cache import close_sqlite, init_sqlite
from app.clients.exceptions import comment_error_handler, CommentFetchingError
from app.clients.reddit import close_reddit_client, start_reddit_client
from app.clients.spaces import download_spaces_files, start_spaces_client, weight_dir_check
from app.router import api, webpage
from ml.sentiment.inference import sentiment_load_model, sentiment_load_tokenizer

DEBUG_LOGS = os.environ.get("DEBUG_LOGS", "0") == "1"

@asynccontextmanager
async def lifespan(app: FastAPI):

    level = logging.DEBUG if DEBUG_LOGS else logging.INFO
    logging.basicConfig(
        level=level,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%H:%M:%S",
    )
    logging.getLogger("prawcore").setLevel(logging.WARNING)
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("botocore").setLevel(logging.WARNING)
    logging.getLogger("python_multipart").setLevel(logging.WARNING)

    load_dotenv()

    spaces_client = start_spaces_client()
    weight_dir_check()
    download_spaces_files(spaces_client=spaces_client)
    con = init_sqlite()

    reddit = start_reddit_client()
    model_session = sentiment_load_model()
    tokenizer = sentiment_load_tokenizer()

    state_data = {
        "con": con,
        "model_session": model_session, 
        "reddit": reddit,
        "tokenizer": tokenizer
    }

    yield state_data

    close_sqlite(con=con)
    await close_reddit_client(reddit=reddit)


app = FastAPI(lifespan=lifespan, docs_url=None, redoc_url=None)
app.add_exception_handler(CommentFetchingError, comment_error_handler)
app.include_router(router=api.router)
app.include_router(router=webpage.router)


if __name__ == "__main__":
    uvicorn.run("app.main:app", port=5000, reload=True)