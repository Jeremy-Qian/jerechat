import random
import streamlit as st
from constants import MODEL_15PRO, MODEL_RAMPION2


def get_random_model_order():
    """
    Get random order for displaying models in side-by-side comparison.
    
    Returns:
        tuple: (left_model, right_model) where each is either MODEL_15PRO or MODEL_RAMPION2
    """
    models = [MODEL_15PRO, MODEL_RAMPION2]
    random.shuffle(models)
    return models[0], models[1]


def get_model_order():
    """Get a random model order for this message."""
    left, right = get_random_model_order()
    return left, right


