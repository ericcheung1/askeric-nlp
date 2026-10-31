import logging
import os
from contextlib import asynccontextmanager

import uvicorn
from dotenv import load_dotenv
from fastapi import FastAPI

from app.clients.cache import (
    close_sqlite,
    init_sqlite,
    load_saved_posts,
    write_many_to_table,
)
from app.clients.exceptions import CommentFetchingError, comment_error_handler
from app.clients.reddit import close_reddit_client, start_reddit_client
from app.router import api, webpage
from ml.nltk.load import sentiment_load_model
from ml.yake.load import keyword_load_model

DEBUG_LOGS = os.environ.get("DEBUG_LOGS", "0") == "1"


@asynccontextmanager
async def lifespan(app: FastAPI):
    level = logging.DEBUG if DEBUG_LOGS else logging.INFO
    logging.basicConfig(
        level=level,
        format="%(asctime)s [PID:%(process)d] [%(levelname)s] %(name)s: %(message)s",
        datefmt="%H:%M:%S",
    )
    logging.getLogger("prawcore").setLevel(logging.WARNING)
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("botocore").setLevel(logging.WARNING)
    logging.getLogger("python_multipart").setLevel(logging.WARNING)

    load_dotenv()

    con = init_sqlite()
    saved_posts, urls = load_saved_posts()
    write_many_to_table(data=saved_posts, con=con)

    reddit = start_reddit_client()

    sia = sentiment_load_model()
    yake = keyword_load_model()

    state_data = {
        "con": con,
        "reddit": reddit,
        "sia": sia,
        "urls": urls,
        "yake": yake,
    }

    yield state_data

    close_sqlite(con=con)
    await close_reddit_client(reddit=reddit)


app = FastAPI(lifespan=lifespan)
app.add_exception_handler(CommentFetchingError, comment_error_handler)
app.include_router(router=api.router)
app.include_router(router=webpage.router, include_in_schema=False)


if __name__ == "__main__":
    uvicorn.run("app.main:app", port=5000, reload=True)
