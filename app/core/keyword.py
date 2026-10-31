def score_keywords(yake, text_inputs):

    output_list = []

    for text in text_inputs:

        keywords = yake.extract_keywords(text)
        save = []

        for keyword, score in keywords:
            save.append((keyword, float(score)))            
            
        output_list.append(save)

    return output_list

if __name__ == "__main__":
    text_inputs = [
        "‘Small’ ‘patellar’ ‘tear’ on scrawny giant dweeb. Much longer than 10 weeks are they on crack?!?",
        "Hey let’s just call a league-wide truce and have everyone get their surgeries taken care of right now. We can all have our benches duke it out for 1-3 months and finish strong with the big dawgs.",
        "Maxing Chet and JDub who at this point have both earned the injury-prone label might be what takes this thing down."
    ]

    from ml.yake.load import keyword_load_model

    yake = keyword_load_model()

    keywords = score_keywords(yake=yake, text_inputs=text_inputs)
    print(keywords)
