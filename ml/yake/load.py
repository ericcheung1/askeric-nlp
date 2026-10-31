import yake

def keyword_load_model():
    kw_extractor = yake.KeywordExtractor(
        lan="en",
        top=10,
        n=3
    )

    return kw_extractor