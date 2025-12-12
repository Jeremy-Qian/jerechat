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

def save_feedback(
    message_index: int,
    feedback_type: str,
    chat_history: Optional[List[Dict]] = None,
    user_id: str = "anonymous",
    details: Optional[str] = None,
) -> Optional[Dict[str, Any]]:
    """
    Save user feedback to Supabase.

    Args:
        message_index: Index of the message being reviewed
        feedback_type: Type of feedback ("good" or "bad")
        chat_history: Optional list of chat messages for context
        user_id: User identifier (defaults to "anonymous")
        details: Optional additional feedback details

    Returns:
        Response data from Supabase, or None if save failed
    """
    client = _init_supabase()
    if client is None:
        return None

    try:
        data = {
            "message_index": message_index,
            "feedback_type": feedback_type,
            "chat_history": chat_history if chat_history else [],
            "user_id": user_id,
            "details": details,
        }
        result = client.table("feedback").insert(data).execute()
        return result.data
    except Exception as e:
        st.error(f"Failed to save feedback: {e}")
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

# Explicitly export functions for clarity
__all__ = ['save_feedback', 'get_feedback_stats']
