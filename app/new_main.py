from contextlib import asynccontextmanager
from fastapi import FastAPI
from dotenv import load_dotenv
from app.clients.reddit import authenticate_reddit
from ml.sentiment.inference import sentiment_load_model, sentiment_load_tokenizer
from app.router import index
import uvicorn


@asynccontextmanager
async def lifespan(app: FastAPI):

    load_dotenv()
    app.state.reddit = authenticate_reddit()
    app.state.model_session = sentiment_load_model()
    app.state.tokenizer = sentiment_load_tokenizer()

    yield


app = FastAPI(lifespan=lifespan, docs_url=None, redoc_url=None)
app.include_router(router=index.router)


if __name__ == "__main__":
    uvicorn.run("app.new_main:app", port=5000, reload=True)