def score_keywords(yake, text_inputs):
    """Keyword extraction for both input types"""

    output_list = []

    for text in text_inputs:
        keywords = yake.extract_keywords(text)
        save = []

        for keyword, score in keywords:
            save.append((keyword, float(score)))

        output_list.append(save)

    return output_list
