from contextlib import asynccontextmanager
from fastapi import FastAPI
from dotenv import load_dotenv
from app.clients.reddit import start_reddit_client
from app.clients.spaces import start_spaces_client, weight_dir_check, download_spaces_files
from ml.sentiment.inference import sentiment_load_model, sentiment_load_tokenizer
from app.router import index
import uvicorn
import logging
import os

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

    load_dotenv()

    spaces_client = start_spaces_client()
    weight_dir_check()
    download_spaces_files(spaces_client=spaces_client)

    reddit = start_reddit_client()
    model_session = sentiment_load_model()
    tokenizer = sentiment_load_tokenizer()

    state_data = {
        "reddit": reddit, 
        "model_session": model_session, 
        "tokenizer": tokenizer
    }

    yield state_data


app = FastAPI(lifespan=lifespan, docs_url=None, redoc_url=None)
app.include_router(router=index.router)


if __name__ == "__main__":
    uvicorn.run("app.main:app", port=5000, reload=True)