from typing import Any, Dict, List, Optional
import datetime

import streamlit as st
from supabase import Client, create_client

# Initialize Supabase client with error handling
supabase: Optional[Client] = None

def _init_supabase() -> Optional[Client]:
    """Initialize and return Supabase client, or None if configuration is missing."""
    global supabase

    if supabase is not None:
        return supabase

    try:
        supabase_url = st.secrets.get("supabase_url")
        supabase_key = st.secrets.get("supabase_key")

        if not supabase_url or not supabase_key:
            st.warning(
                "Supabase credentials not configured. Feedback features will be disabled."
            )
            return None

        supabase = create_client(supabase_url, supabase_key)
        return supabase
    except Exception as e:
        st.warning(
            f"Failed to initialize Supabase client: {e}. Feedback features will be disabled."
        )
        return None

def save_preference_feedback(
    message_index: int,
    preferred_model: str,
    other_model: str,
    chat_history: Optional[List[Dict]] = None,
    user_id: str = "anonymous",
    details: Optional[str] = None,
    response_times: Optional[Dict[str, float]] = None,
) -> Optional[Dict[str, Any]]:
    """
    Save preference feedback to Supabase. Preferred model gets 'good', other gets 'bad'.

    Args:
        message_index: Index of the message being reviewed
        preferred_model: Model version user preferred ("1.5pro" or "rampion2")
        other_model: The other model version
        chat_history: Optional list of chat messages for context
        user_id: User identifier (defaults to "anonymous")
        details: Optional additional feedback details
        response_times: Dict with response times for each model

    Returns:
        Response data from Supabase, or None if save failed
    """
    client = _init_supabase()
    if client is None:
        return None

    try:
        # Save feedback for preferred model (good)
        preferred_data = {
            "message_index": message_index,
            "feedback_type": "good",
            "chat_history": chat_history if chat_history else [],
            "user_id": user_id,
            "details": details,
            "model_version": preferred_model,
            "response_time": response_times.get(preferred_model) if response_times else None,
        }
        client.table("feedback").insert(preferred_data).execute()

        # Save feedback for other model (bad)
        other_data = {
            "message_index": message_index,
            "feedback_type": "bad",
            "chat_history": chat_history if chat_history else [],
            "user_id": user_id,
            "details": details,
            "model_version": other_model,
            "response_time": response_times.get(other_model) if response_times else None,
        }
        result = client.table("feedback").insert(other_data).execute()
        return result.data
    except Exception as e:
        st.error(f"Failed to save preference feedback: {e}")
        return None

def get_feedback_stats() -> Dict[str, int]:
    """
    Get feedback statistics.

    Returns:
        Dictionary with 'good' and 'bad' feedback counts
    """
    client = _init_supabase()
    if client is None:
        return {"good": 0, "bad": 0}

    try:
        good_count = (
            client.table("feedback").select("*").eq("feedback_type", "good").execute()
        )
        bad_count = (
            client.table("feedback").select("*").eq("feedback_type", "bad").execute()
        )

        return {
            "good": len(good_count.data) if good_count.data else 0,
            "bad": len(bad_count.data) if bad_count.data else 0,
        }
    except Exception as e:
        st.error(f"Failed to get feedback stats: {e}")
        return {"good": 0, "bad": 0}

def get_model_feedback_stats(model_version: str) -> Dict[str, int]:
    """
    Get feedback statistics for a specific model version.

    Args:
        model_version: Model version to filter by ("1.5pro" or "rampion2")

    Returns:
        Dictionary with 'good' and 'bad' feedback counts for the specified model
    """
    client = _init_supabase()
    if client is None:
        return {"good": 0, "bad": 0}

    try:
        good_count = (
            client.table("feedback")
            .select("*")
            .eq("feedback_type", "good")
            .eq("model_version", model_version)
            .execute()
        )
        bad_count = (
            client.table("feedback")
            .select("*")
            .eq("feedback_type", "bad")
            .eq("model_version", model_version)
            .execute()
        )

        return {
            "good": len(good_count.data) if good_count.data else 0,
            "bad": len(bad_count.data) if bad_count.data else 0,
        }
    except Exception as e:
        st.error(f"Failed to get model feedback stats: {e}")
        return {"good": 0, "bad": 0}

def get_ab_test_results() -> Dict[str, Dict[str, int]]:
    """
    Get A/B test results comparing both model versions.

    Returns:
        Dictionary with feedback stats for each model version
    """
    return {
        "1.5pro": get_model_feedback_stats("1.5pro"),
        "rampion2": get_model_feedback_stats("rampion2"),
    }

def get_response_time_stats(model_version: Optional[str] = None) -> Dict[str, float]:
    """
    Get response time statistics.

    Args:
        model_version: Optional model version to filter by

    Returns:
        Dictionary with average, min, and max response times
    """
    client = _init_supabase()
    if client is None:
        return {"avg": 0.0, "min": 0.0, "max": 0.0}

    try:
        query = client.table("feedback").select("response_time").not_.is_("response_time", "null")
        if model_version:
            query = query.eq("model_version", model_version)
        
        result = query.execute()
        
        if not result.data:
            return {"avg": 0.0, "min": 0.0, "max": 0.0}
        
        response_times = [row["response_time"] for row in result.data if row["response_time"] is not None]
        
        if not response_times:
            return {"avg": 0.0, "min": 0.0, "max": 0.0}
        
        return {
            "avg": sum(response_times) / len(response_times),
            "min": min(response_times),
            "max": max(response_times),
        }
    except Exception as e:
        st.error(f"Failed to get response time stats: {e}")
        return {"avg": 0.0, "min": 0.0, "max": 0.0}

# Explicitly export functions for clarity
__all__ = ['save_feedback', 'get_feedback_stats', 'get_model_feedback_stats', 'get_ab_test_results', 'get_response_time_stats']
