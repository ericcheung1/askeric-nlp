import logging

import yake

logger = logging.getLogger(__name__)


def keyword_load_model():
    """Loads yake keyword extraction model"""
    try:
        kw_extractor = yake.KeywordExtractor(lan="en", top=10, n=2)

        return kw_extractor
    except Exception as e:
        logger.critical(f"{e!s} in 'keyword_load_model")
        raise RuntimeError
