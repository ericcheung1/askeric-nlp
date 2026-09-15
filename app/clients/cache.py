import json
import logging
from pathlib import Path
import sqlite3

logger = logging.getLogger(__name__)

def init_sqlite():
    """Initialized sqlite and creates table"""

    DB_DIR = Path("app/data")
    DB_DIR.mkdir(exist_ok=True)
    DB_PATH = Path(DB_DIR, "cache.db")
    con = sqlite3.connect(DB_PATH)

    try:
        with con:
            con.execute("PRAGMA journal_mode = WAL")

            query = """
                CREATE TABLE IF NOT EXISTS cache (
                    submission_id TEXT PRIMARY KEY,
                    comment_tree TEXT NOT NULL,
                    overall_sentiment TEXT NOT NULL
                );
            """
            con.execute(query)
            con.commit()

        logger.info("Successfully Initialized Cache in 'init_sqlite'")

        return con
    
    except sqlite3.Error as e:
        logger.critical(f"{str(e)} in 'init_sqlite'")
        raise RuntimeError


def close_sqlite(con):
    """Closes sqlite connection"""
    con.close()


def query_from_table(submission_id, con):
    """Queries database table for post and analysis results"""

    try:
        query = "SELECT comment_tree, overall_sentiment FROM cache WHERE submission_id = ?;"
        cur = con.execute(query, (submission_id,))
        query_result = cur.fetchone()

    except sqlite3.Error as e:
        logger.warning(f"{str(e)} in 'query_from_table'")
        query_result = None

    if query_result is None:
        comment_tree = None
        overall_sentiment = None
        logger.info("Post Not Cached in Database Table in 'query_from_table'")

    else:
        comment_tree = json.loads(query_result[0])
        overall_sentiment = json.loads(query_result[1])
        logger.info("Post Found in Database Table in 'query_from_table'")

    return comment_tree, overall_sentiment


def write_to_table(submission_id, comment_tree, overall_sentiment, con):
    """Caches post and analysis results in database table"""

    comment_tree_str = json.dumps(comment_tree, default=str)
    overall_sentiment_str = json.dumps(overall_sentiment, default=str)

    try:
        with con:
            query = "INSERT INTO cache (submission_id, comment_tree, overall_sentiment) VALUES (?, ?, ?);"
            con.execute(query, (submission_id, comment_tree_str, overall_sentiment_str))
            con.commit()
            logger.info("Successfully Cached Post to Database Table in 'write_to_table'")

    except sqlite3.Error as e:
        logger.warning(f"{str(e)} in 'write_to_table'")