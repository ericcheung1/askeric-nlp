from contextlib import asynccontextmanager
from fastapi import FastAPI
from dotenv import load_dotenv
from app.clients.reddit import authenticate_reddit
from ml.sentiment.inference import sentiment_load_model, sentiment_load_tokenizer
from app.router import index
import uvicorn
import logging
import os

DEBUG_LOGS = os.environ.get("DEBUG_LOGS", "0") == "1"

@asynccontextmanager
async def lifespan(app: FastAPI):

    load_dotenv()
    app.state.reddit = authenticate_reddit()
    app.state.model_session = sentiment_load_model()
    app.state.tokenizer = sentiment_load_tokenizer()

    yield


level = logging.DEBUG if DEBUG_LOGS else logging.INFO
logging.basicConfig(
    level=level,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%H:%M:%S",
)
logging.getLogger("prawcore").setLevel(logging.WARNING)
logging.getLogger("urllib3").setLevel(logging.WARNING)


app = FastAPI(lifespan=lifespan, docs_url=None, redoc_url=None)
app.include_router(router=index.router)


if __name__ == "__main__":
    uvicorn.run("app.main:app", port=5000, reload=True)