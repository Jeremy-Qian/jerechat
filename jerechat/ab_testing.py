import random
import streamlit as st
from datetime import datetime
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
    """Get the current model order for this session."""
    if 'model_order' not in st.session_state:
        left, right = get_random_model_order()
        st.session_state.model_order = (left, right)
        st.session_state.model_order_timestamp = datetime.now().isoformat()
    return st.session_state.model_order


def reset_model_order():
    """Reset the model order (for testing)."""
    if 'model_order' in st.session_state:
        del st.session_state.model_order
    if 'model_order_timestamp' in st.session_state:
        del st.session_state.model_order_timestamp
