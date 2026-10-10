import json
import logging
import sqlite3
from pathlib import Path

logger = logging.getLogger(__name__)

DATA_DIRECTORY = Path("app/data")

def init_sqlite():
    """Initialized sqlite and creates table"""

    DATA_DIRECTORY.mkdir(exist_ok=True)
    DB_PATH = Path(DATA_DIRECTORY, "cache.db")
    con = sqlite3.connect(DB_PATH, check_same_thread=False)

    try:
        with con:
            con.execute("PRAGMA journal_mode = WAL")

            query = """
                CREATE TABLE IF NOT EXISTS cache (
                    submission_id TEXT PRIMARY KEY,
                    comment_tree TEXT NOT NULL,
                    overall_sentiment TEXT NOT NULL,
                    post_data TEXT NOT NULL
                );
            """
            con.execute(query)
            con.commit()

        logger.info("Successfully Initialized Cache in 'init_sqlite'")

        return con

    except sqlite3.Error as e:
        logger.critical(f"{e!s} in 'init_sqlite'")
        raise RuntimeError


def read_seed_data():

    DATA_DIRECTORY.mkdir(exist_ok=True)
    data = []

    for file_path in DATA_DIRECTORY.glob("*.json"):
        with open(file_path, "r", encoding="utf-8") as file:
            post = json.load(file)

        submission_id = post["submission_id"]
        comment_tree = json.dumps(post["comment_tree"], default=str)
        overall_sentiment = json.dumps(post["overall_sentiment"], default=str)
        post_data = json.dumps(post["post_data"], default=str)

        data.append((submission_id, comment_tree, overall_sentiment, post_data))

    logger.debug("data: %s", data)
    logger.info("successfully read seed data in 'read_seed_data'")

    return data


def close_sqlite(con):
    """Closes sqlite connection"""
    con.close()


def query_from_table(submission_id, con):
    """Queries database table for post and analysis results"""

    try:
        query = "SELECT comment_tree, overall_sentiment, post_data FROM cache WHERE submission_id = ?;"
        cur = con.execute(query, (submission_id,))
        query_result = cur.fetchone()

    except sqlite3.Error as e:
        logger.warning(f"{e!s} in 'query_from_table'")
        query_result = None

    if query_result is None:
        comment_tree = None
        overall_sentiment = None
        post_data = None
        logger.info("Post Not Cached in Database Table in 'query_from_table'")

    else:
        comment_tree = json.loads(query_result[0])
        overall_sentiment = json.loads(query_result[1])
        post_data = json.loads(query_result[2])
        logger.info("Post Found in Database Table in 'query_from_table'")

    return comment_tree, overall_sentiment, post_data


def write_to_table(submission_id, comment_tree, overall_sentiment, post_data, con):
    """Caches post and analysis results in database table"""

    comment_tree_str = json.dumps(comment_tree, default=str)
    overall_sentiment_str = json.dumps(overall_sentiment, default=str)
    post_data_str = json.dumps(post_data, default=str)

    try:
        with con:
            query = """
                INSERT INTO cache (
                    submission_id, 
                    comment_tree, 
                    overall_sentiment,
                    post_data
                ) 
                VALUES (?, ?, ?, ?)
                ON CONFLICT(submission_id) DO NOTHING;
            """
            con.execute(
                query,
                (submission_id, comment_tree_str, overall_sentiment_str, post_data_str),
            )
            con.commit()
            logger.info(
                "Successfully Cached Post to Database Table in 'write_to_table'"
            )

    except sqlite3.Error as e:
        logger.warning(f"{e!s} in 'write_to_table'")


def write_many_to_table(data, con):
    try:
        with con:
            query = """
                INSERT INTO cache (
                    submission_id, 
                    comment_tree, 
                    overall_sentiment,
                    post_data
                ) 
                VALUES (?, ?, ?, ?)
                ON CONFLICT(submission_id) DO NOTHING;
            """
            con.executemany(
                query,
                data
            )
            con.commit()
            logger.info(
                "Successfully Cached Post to Database Table in 'write_many_to_table'"
            )

    except sqlite3.Error as e:
        logger.warning(f"{e!s} in 'write_many_to_table'")