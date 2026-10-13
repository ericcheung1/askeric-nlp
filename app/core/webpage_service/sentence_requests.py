def clean_sentence_input(input):
    """Cleans input for sentence request type"""
    input.strip()


def format_sentence_input(input):
    """Formats input for sentence request type"""
    return [input]


def format_sentence_output(output):
    """Formats sentiment label and confidence output for sentence request type"""

    if output[0] >= 0.05:
        label = "POSITIVE"
    elif output[0] <= -0.05:
        label = "NEGATIVE"
    else:
        label = "NEUTRAL"

    return label, output[0]
