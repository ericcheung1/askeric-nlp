def score_sentiment(sia, text_inputs):
    """Sentiment scoring for both request type"""

    output_list = []

    for text in text_inputs:
        sia_output = sia.polarity_scores(text)
        output_list.append(sia_output["compound"])

    return output_list
