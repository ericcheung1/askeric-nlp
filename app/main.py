import logging
import os
from contextlib import asynccontextmanager

import uvicorn
from dotenv import load_dotenv
from fastapi import FastAPI

from app.clients.cache import close_sqlite, init_sqlite
from app.clients.exceptions import CommentFetchingError, comment_error_handler
from app.clients.reddit import close_reddit_client, start_reddit_client
from app.clients.spaces import (
    download_spaces_files,
    start_spaces_client,
    weight_dir_check,
)
from app.core.inference_process import start_inference_process
from app.router import api, webpage

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

    spaces_client = start_spaces_client()
    weight_dir_check()
    download_spaces_files(spaces_client=spaces_client)
    con = init_sqlite()
    reddit = start_reddit_client()

    task_queue, result_queue, inference_process = start_inference_process()

    state_data = {
        "con": con,
        "reddit": reddit,
        "result_queue": result_queue,
        "task_queue": task_queue,
        "inference_process": inference_process,
    }

    yield state_data

    task_queue.put(None)

    task_queue.close()
    task_queue.join_thread()
    result_queue.close()
    result_queue.join_thread()

    inference_process.join(timeout=2)
    if inference_process.is_alive():
        inference_process.terminate()
        inference_process.join()

    close_sqlite(con=con)
    await close_reddit_client(reddit=reddit)


app = FastAPI(lifespan=lifespan)
app.add_exception_handler(CommentFetchingError, comment_error_handler)
app.include_router(router=api.router)
app.include_router(router=webpage.router, include_in_schema=False)


if __name__ == "__main__":
    uvicorn.run("app.main:app", port=5000, reload=True)
