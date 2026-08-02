from app.schemas.input import UserInputs

def clean_user_inputs(user_inputs: UserInputs):

    cleaned_inputs = []

    for user_input in user_inputs:
        text = user_input.text
        cleaned_text = text.lower().strip()
        id = text.text_id

        cleaned_inputs.append({
            id: cleaned_text
        })

    return cleaned_inputs


def prepare_model_inputs(processed_inputs):
    model_inputs = []
    for id, text in processed_inputs.items():
        model_inputs.append(text)

    return model_inputs


