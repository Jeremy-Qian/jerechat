from supabase import create_client, Client
import os
import streamlit as st

# Initialize Supabase client
supabase_url = st.secrets.get("supabase_url")
supabase_key = st.secrets.get("supabase_key")

supabase: Client = create_client(supabase_url, supabase_key)

def save_feedback(message_index: int, feedback_type: str, chat_history: list = None, user_id: str = "anonymous"):
    """Save user feedback to Supabase"""
    data = {
        "message_index": message_index,
        "feedback_type": feedback_type,  # "good" or "bad"
        "chat_history": chat_history if chat_history else [],
        "user_id": user_id
    }
    return supabase.table("feedback").insert(data).execute()

def get_feedback_stats():
    """Get feedback statistics"""
    try:
        good_count = supabase.table("feedback").select("*").eq("feedback_type", "good").execute()
        bad_count = supabase.table("feedback").select("*").eq("feedback_type", "bad").execute()
        
        return {
            "good": len(good_count.data) if good_count.data else 0,
            "bad": len(bad_count.data) if bad_count.data else 0
        }
    except:
        return {"good": 0, "bad": 0}