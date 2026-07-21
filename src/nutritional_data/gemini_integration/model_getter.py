from dto.gemini_model_data import GeminiModelDTO
from interact_db.get_data_from_db import get_gemini_models
from interact_db.update_gemini_model import update_is_blocked_gemini_models

def get_gemini_model() -> GeminiModelDTO:
    available_gemini_models = get_gemini_models()

    models_to_update = []
    model_to_return = None

    for model in available_gemini_models:
        if model.get_is_blocked():
            if model.get_hours_since_last_petition() > 24:
                model.set_is_blocked(False)
                models_to_update.append(model)
            else:
                continue

        model_to_return = model
        break

    if models_to_update:
        update_is_blocked_gemini_models(models_to_update)

    if not model_to_return:
        raise Exception("No gemini models available now.")

    return model_to_return

