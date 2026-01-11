import streamlit as st
import streamlit.components.v1 as components
import datetime
import time
import jerechat as jc
from typing import Any, Dict, List, Optional
from supabase import Client, create_client
from jerechat import ab_testing, rampion2_model
from database import save_preference_feedback, save_original_feedback, get_ab_test_results, get_response_time_stats
from constants import MODEL_15PRO, MODEL_RAMPION2, MODEL_15PRO_DISPLAY, MODEL_RAMPION2_DISPLAY, DEFAULT_CHECKPOINT_PATH, SUGGESTIONS

st.set_page_config(
    page_title="JereChat", 
    page_icon="✨",
    initial_sidebar_state="expanded"
)

# Add smooth transitions CSS
st.markdown("""
<style>
/* Smooth transitions for preference selection */
.preference-container {
    transition: all 0.3s ease;
    opacity: 1;
}

.preference-loading {
    opacity: 0.7;
    pointer-events: none;
}

.preference-button {
    transition: all 0.2s ease;
}

.preference-button:hover {
    transform: translateY(-1px);
}

/* Smooth fade for model reveal */
.model-reveal {
    animation: fadeIn 0.5s ease-in;
}

@keyframes fadeIn {
    from { opacity: 0; transform: translateY(10px); }
    to { opacity: 1; transform: translateY(0); }
}

/* Hide running indicator during preference selection */
.stStatusContainer { display: none; }
</style>
""", unsafe_allow_html=True)

# Inject Umami analytics tracking script into header
components.html(
    """
    <script defer src="https://cloud.umami.is/script.js" data-website-id="f401341a-02f5-49e7-a16a-145dd36cec93"></script>
    """,
    height=0
)

def check_invitation_code():
    """Check if user has entered a valid and not expired invitation code."""
    if 'invitation_verified' not in st.session_state:
        st.session_state.invitation_verified = False
        st.session_state.active_code = None
    
    if not st.session_state.invitation_verified:
        # Get valid codes from secrets
        valid_codes = st.secrets.get("invitation_codes", [])
        if not valid_codes:
            st.error("No valid invitation codes found in secrets!")
            st.stop()
            
        # Create a non-closable popup
        st.markdown("""
            <style>
                .stAlert {
                    z-index: 1000;
                }
                .stDialog {
                    z-index: 1001;
                }
                .stTextInput {
                    z-index: 1002;
                }
                .expired {
                    color: #ff4b4b;
                    font-weight: bold;
                }
                .valid {
                    color: #00cc00;
                }
                .stTextInput > div > div > input {
                    text-align: center;
                }
            </style>
        """, unsafe_allow_html=True)
        
        # Show invitation code entry form in main area
        st.markdown("## :material/lock_person: Enter Invitation Code")
        st.warning("We are sorry, but JereChat is not completely open right now.\
            You can get access only by invitation codes.", icon=":material/lock:")
        
        with st.form("invitation_form"):
            col1, col2, col3 = st.columns([1, 1, 1])
            with col2:
                code = st.text_input("Enter your 6-digit code:", max_chars=6, type="default")
            with col2:
                submitted = st.form_submit_button("Submit")
            
            if submitted:
                code_found = False
                today = datetime.date.today()
                
                for code_info in valid_codes:
                    if code == code_info['code_number']:
                        code_found = True
                        expiry_date = datetime.datetime.strptime(code_info['code_expiry_date'], "%Y-%m-%d").date()
                        if today > expiry_date:
                            st.error(f"❌ This invitation code expired on {expiry_date}. Please request a new one.")
                        else:
                            st.session_state.invitation_verified = True
                            st.session_state.active_code = code_info
                            st.rerun()
                        break
                
                if not code_found:
                    st.error("❌ Invalid invitation code. Please try again.")
        
        with st.sidebar:
            st.markdown("## Don't have an invitation code?")
            st.info("Please contact Jeremy to obtain an invitation code.")
        
        # Prevent the rest of the app from running
        st.stop()

# Check invitation code before showing the app
check_invitation_code()

# -----------------------------------------------------------------------------
# Sidebar with 'My Code' section
with st.sidebar:
    st.markdown("## My Code")
    if 'active_code' in st.session_state and st.session_state.active_code:
        code_info = st.session_state.active_code
        expiry_date = datetime.datetime.strptime(code_info['code_expiry_date'], "%Y-%m-%d").date()
        today = datetime.date.today()
        days_remaining = (expiry_date - today).days
        
        status = "✅ Valid" if today <= expiry_date else "❌ Expired"
        status_color = "green" if today <= expiry_date else "red"
        
        st.markdown(f"""#### You have an invite code. See below for more info.""")
        st.markdown(f"### Invitation Code Details")
        with st.expander(f"**Click to see code:**", expanded=False):
            st.write(f"**{code_info['code_number']}**")
        st.markdown(f"**Status:** <span style='color:{status_color}'>{status}</span>", unsafe_allow_html=True)
        st.markdown(f"**Notes:** {code_info['code_notes']}")
        st.markdown(f"**Expiry Date:** {expiry_date.strftime('%B %d, %Y')}")
            
        if today <= expiry_date:
            st.markdown(f"**Expires in:** {days_remaining} days")
        else:
            st.error("This code has expired. Please contact support for a new invitation code.")
    else:
        st.markdown("No active invitation code found.")
    
    st.divider()
    
    # A/B Testing Monitoring Dashboard
    with st.expander("📊 A/B Test Dashboard", expanded=False):
        st.markdown("### Preference Stats")
        try:
            ab_results = get_ab_test_results()
            
            col1, col2 = st.columns(2)
            with col1:
                st.markdown(f"#### {MODEL_15PRO_DISPLAY}")
                st.metric("👍 Preferred", ab_results[MODEL_15PRO]["good"])
                st.metric("👎 Not Preferred", ab_results[MODEL_15PRO]["bad"])
            
            with col2:
                st.markdown(f"#### {MODEL_RAMPION2_DISPLAY}")
                st.metric("👍 Preferred", ab_results[MODEL_RAMPION2]["good"])
                st.metric("👎 Not Preferred", ab_results[MODEL_RAMPION2]["bad"])
            
            # Calculate preference rate
            total_15pro = ab_results[MODEL_15PRO]["good"] + ab_results[MODEL_15PRO]["bad"]
            total_r2 = ab_results[MODEL_RAMPION2]["good"] + ab_results[MODEL_RAMPION2]["bad"]
            
            if total_15pro > 0:
                rate_15pro = (ab_results[MODEL_15PRO]["good"] / total_15pro) * 100
                st.metric(f"{MODEL_15PRO_DISPLAY} Preference Rate", f"{rate_15pro:.1f}%")
            
            if total_r2 > 0:
                rate_r2 = (ab_results[MODEL_RAMPION2]["good"] / total_r2) * 100
                st.metric(f"{MODEL_RAMPION2_DISPLAY} Preference Rate", f"{rate_r2:.1f}%")
            
            st.markdown("---")
            st.markdown("### Response Times")
            r2_times = get_response_time_stats(MODEL_RAMPION2)
            pro_times = get_response_time_stats(MODEL_15PRO)
            
            col3, col4 = st.columns(2)
            with col3:
                st.markdown(f"#### {MODEL_15PRO_DISPLAY}")
                st.metric("Avg", f"{pro_times['avg']:.3f}s")
            
            with col4:
                st.markdown(f"#### {MODEL_RAMPION2_DISPLAY}")
                st.metric("Avg", f"{r2_times['avg']:.3f}s")
        except Exception as e:
            st.warning(f"Could not load stats: {e}")

# -----------------------------------------------------------------------------
# Constants (keeping UI-related constants)
HISTORY_LENGTH = 5
DEBUG_MODE = st.query_params.get("debug", "false").lower() == "true"

# -----------------------------------------------------------------------------
# Model response generation

def get_response(prompt, model_version):
    """Generate response using specified model"""
    start_time = time.time()
    
    try:
        if model_version == MODEL_RAMPION2:
            checkpoint_path = st.secrets.get("rampion2_checkpoint_path", DEFAULT_CHECKPOINT_PATH)
            
            if 'rampion2_model' not in st.session_state:
                with st.spinner("Loading Rampion 2 model..."):
                    searcher, voc = rampion2_model.load_model(checkpoint_path)
                    if searcher and voc:
                        st.session_state.rampion2_model = (searcher, voc)
                    else:
                        return None, None
            
            searcher, voc = st.session_state.rampion2_model
            normalized_prompt = rampion2_model.normalizeString(prompt)
            response_text = rampion2_model.generate_response(searcher, voc, normalized_prompt)
        else:
            response_text = jc.generate_response(prompt, "1.5")
        
        response_time = time.time() - start_time
        
        response_text = response_text.replace("||", "  \n\n")
        return response_text, response_time
    except Exception as e:
        return None, None

# -----------------------------------------------------------------------------
# UI rendering helpers (to simplify duplicate rendering logic)

def get_model_display_name(model_id: str) -> str:
    """Convert model identifier to display name for UI."""
    if model_id == MODEL_15PRO:
        return MODEL_15PRO_DISPLAY
    elif model_id == MODEL_RAMPION2:
        return MODEL_RAMPION2_DISPLAY
    return model_id


def get_user_id() -> str:
    """Return the current user's id from session state or 'anonymous'."""
    return (
        st.session_state.active_code.get('code_number', 'anonymous')
        if 'active_code' in st.session_state and st.session_state.active_code
        else 'anonymous'
    )


def get_response_times(message_index: int) -> Dict[str, float]:
    """Return response times dict for a given message index from session state."""
    return st.session_state.get(f'response_times_{message_index}', {})


def render_user_message(content: str) -> None:
    """Render a user message bubble."""
    with st.chat_message("user"):
        st.text(content)


def render_preferred_message(message: Dict[str, Any]) -> None:
    """Render a previously preferred single-model assistant message."""
    with st.chat_message("assistant", avatar="data/resources/icon_small.png"):
        model_name = get_model_display_name(message.get("model", "Unknown"))
        st.markdown(f"**{model_name}**")
        st.markdown(message.get("content", ""))


def render_comparison_message(
    index: int,
    left_model: str,
    right_model: str,
    left_response: str,
    right_response: str,
    show_buttons: bool = True,
) -> None:
    """Render side-by-side assistant responses. Labels are hidden until reveal."""
    revealed = st.session_state.get(f"revealed_{index}", None)
    
    # Check if this message is being processed
    processing_key = f'processing_{index}'
    is_processing = st.session_state.get(processing_key, False)

    # If a preference was made, show only the preferred side
    if revealed and revealed.get("show_only_preferred"):
        # Add smooth transition class
        transition_class = "model-reveal" if not is_processing else "preference-loading"
        
        with st.chat_message("assistant", avatar="data/resources/icon_small.png"):
            preferred_display = get_model_display_name(revealed['preferred'])
            other_display = get_model_display_name(revealed['other'])
            st.markdown(f"**{preferred_display}**")
            if revealed["preferred"] == left_model:
                st.markdown(left_response)
            else:
                st.markdown(right_response)
        return

    # Otherwise show both sides, masking model names if not yet revealed
    # Add processing state to container
    container_class = "preference-loading" if is_processing else "preference-container"
    
    st.markdown(f'<div class="{container_class}">', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        with st.chat_message("assistant", avatar="data/resources/icon_small.png"):
            left_display = get_model_display_name(left_model) if revealed else "Model A"
            st.markdown(f"**{left_display}**")
            st.markdown(left_response)

    with col2:
        with st.chat_message("assistant", avatar="data/resources/icon_small.png"):
            right_display = get_model_display_name(right_model) if revealed else "Model B"
            st.markdown(f"**{right_display}**")
            st.markdown(right_response)

    st.markdown('</div>', unsafe_allow_html=True)

    # Show preference buttons only when not yet revealed and enabled
    if not revealed and show_buttons:
        show_preference_buttons(index, left_model, right_model)


def render_history_message(index: int, message: Dict[str, Any]) -> None:
    """Render a single message from chat history based on its role/type."""
    if message["role"] == "user":
        render_user_message(message.get("content", ""))
        return

    # Assistant messages can be either comparison or preferred-only
    if "model_order" in message:
        left_model, right_model = message.get("model_order", ab_testing.get_model_order())
        left_response = message.get("left_response", "")
        right_response = message.get("right_response", "")
        render_comparison_message(index, left_model, right_model, left_response, right_response)
    else:
        render_preferred_message(message)

# ORIGINAL FEEDBACK CONTROLS (commented out, kept for reference)
# def show_feedback_controls(message_index):
#     """Shows the "How did I do?" control."""
#     st.write("")
#     
#     with st.popover("How did I do?"):
#         with st.form(key=f"feedback-{message_index}", border=False):
#             with st.container(gap=None):
#                 st.markdown(":small[Rating]")
#                 rating = st.feedback(options="stars")
#             
#             details = st.text_area("More information (optional)")
#             
#             if st.checkbox("Include chat history with my feedback", True):
#                 relevant_history = st.session_state.messages[:message_index + 1]
#             else:
#                 relevant_history = []
#             
#             ""  # Add some space
#             
#             if st.form_submit_button("Send feedback"):
#                 # Save feedback to Supabase
#                 feedback_type = "good" if rating and rating >= 3 else "bad"
#                 chat_history = relevant_history if 'relevant_history' in locals() and relevant_history else []
#                 try:
#                     from database import save_original_feedback
#                     # Get user_id from session state or use anonymous
#                     user_id = st.session_state.active_code.get('code_number', 'anonymous') if 'active_code' in st.session_state and st.session_state.active_code else 'anonymous'
#                     save_original_feedback(message_index, feedback_type, chat_history, user_id=user_id, details=details)
#                     st.toast("#####  Thank you for your feedback!", icon=":material/sentiment_very_satisfied:", duration="long")
#                 except Exception as e:
#                     st.toast(f"Error saving feedback: {e}", icon=":material/error:")

def show_preference_buttons(message_index, left_model, right_model):
    """Shows preference buttons for side-by-side comparison."""
    st.write("")
    
    # Check if this preference is currently being processed
    processing_key = f'processing_{message_index}'
    is_processing = st.session_state.get(processing_key, False)
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Disable button during processing and show loading state
        button_disabled = is_processing
        button_help = "Processing..." if is_processing else ""
        
        if st.button(
            f"left is better", 
            key=f"prefer-left-{message_index}", 
            use_container_width=True,
            disabled=button_disabled,
            help=button_help
        ):
            # Set processing state immediately
            st.session_state[processing_key] = True
            # Batch all operations
            save_preference_smooth(message_index, left_model, right_model)
    
    with col2:
        # Disable button during processing and show loading state
        button_disabled = is_processing
        button_help = "Processing..." if is_processing else ""
        
        if st.button(
            f"right is better", 
            key=f"prefer-right-{message_index}", 
            use_container_width=True,
            disabled=button_disabled,
            help=button_help
        ):
            # Set processing state immediately
            st.session_state[processing_key] = True
            # Batch all operations
            save_preference_smooth(message_index, right_model, left_model)

def save_preference_smooth(message_index, preferred_model, other_model):
    """Smooth preference save with optimized state management."""
    try:
        user_id = get_user_id()
        chat_history = st.session_state.messages[:message_index + 1] if 'messages' in st.session_state else []
        response_times = get_response_times(message_index)
        
        # Update UI state first for immediate feedback
        preferred_display = get_model_display_name(preferred_model)
        
        # Update chat history immediately
        if message_index < len(st.session_state.messages):
            message = st.session_state.messages[message_index]
            if message["role"] == "assistant":
                left_model, right_model = message.get("model_order", (None, None))
                left_response = message.get("left_response", "")
                right_response = message.get("right_response", "")
                
                # Keep only the preferred response
                preferred_response = left_response if preferred_model == left_model else right_response
                
                # Update the message to show only preferred response
                st.session_state.messages[message_index] = {
                    "role": "assistant",
                    "content": preferred_response,
                    "model": preferred_model,
                    "was_comparison": True,
                    "other_model": other_model
                }
        
        # Set reveal state
        st.session_state[f'revealed_{message_index}'] = {
            'preferred': preferred_model,
            'other': other_model,
            'show_only_preferred': True
        }
        
        # Clear processing state
        processing_key = f'processing_{message_index}'
        st.session_state[processing_key] = False
        
        # Show success toast
        st.toast(f"#####  You liked {preferred_display}!", icon=":material/sentiment_very_satisfied:", duration="long")
        
        # Save to database in background (non-blocking)
        save_preference_feedback(
            message_index=message_index,
            preferred_model=preferred_model,
            other_model=other_model,
            chat_history=chat_history,
            user_id=user_id,
            response_times=response_times
        )
        
        # Rerun to show updated UI
        st.rerun()
        
    except Exception as e:
        # Clear processing state on error
        processing_key = f'processing_{message_index}'
        st.session_state[processing_key] = False
        st.toast(f"Error saving preference: {e}", icon=":material/error:")
        st.rerun()

def reveal_models(message_index, preferred_model, other_model):
    """Reveal which models were which after preference is chosen."""
    st.session_state[f'revealed_{message_index}'] = {
        'preferred': preferred_model,
        'other': other_model,
        'show_only_preferred': True
    }
    st.rerun()

def save_preference(message_index, preferred_model, other_model):
    """Save user preference to Supabase and update chat history."""
    try:
        user_id = get_user_id()
        chat_history = st.session_state.messages[:message_index + 1] if 'messages' in st.session_state else []
        
        # Get response times from session state
        response_times = get_response_times(message_index)
        
        save_preference_feedback(
            message_index=message_index,
            preferred_model=preferred_model,
            other_model=other_model,
            chat_history=chat_history,
            user_id=user_id,
            response_times=response_times
        )
        preferred_display = get_model_display_name(preferred_model)
        st.toast(f"#####  You liked {preferred_display}!", icon=":material/sentiment_very_satisfied:", duration="long")
        
        # Update chat history to only show preferred response
        if message_index < len(st.session_state.messages):
            message = st.session_state.messages[message_index]
            if message["role"] == "assistant":
                left_model, right_model = message.get("model_order", (None, None))
                left_response = message.get("left_response", "")
                right_response = message.get("right_response", "")
                
                # Keep only the preferred response
                preferred_response = left_response if preferred_model == left_model else right_response
                
                # Update the message to show only preferred response
                st.session_state.messages[message_index] = {
                    "role": "assistant",
                    "content": preferred_response,
                    "model": preferred_model,
                    "was_comparison": True,
                    "other_model": other_model
                }
    except Exception as e:
        st.toast(f"Error saving preference: {e}", icon=":material/error:")

@st.dialog("Disclaimer")
def show_disclaimer_dialog():
    st.caption("""
        Using this chatbot means that you agree to the following:
        - You have read this disclaimer and fully understand;
        - You understand that answers may be inaccurate, and you are willing to recieve the responses;
        - You understand that the developer is not responsible for any damage or loss caused by this chatbot.
    """)

# -----------------------------------------------------------------------------
# Draw the UI

st.badge(""":material/science: Experimental""")

title_row = st.container(
    horizontal=True,
    vertical_alignment="bottom",
)

with title_row:
    st.title(
        "JereChat",
        anchor=False,
        width="stretch",
    )

user_just_asked_initial_question = (
    "initial_question" in st.session_state and st.session_state.initial_question
)

user_just_clicked_suggestion = (
    "selected_suggestion" in st.session_state and st.session_state.selected_suggestion
)

user_first_interaction = (
    user_just_asked_initial_question or user_just_clicked_suggestion
)

has_message_history = (
    "messages" in st.session_state and len(st.session_state.messages) > 0
)

# Show a different UI when the user hasn't asked a question yet.
if not user_first_interaction and not has_message_history:
    st.session_state.messages = []
    
    with st.container():
        st.chat_input("Ask a question...", key="initial_question")

        selected_suggestion = st.pills(
            label="Examples",
            label_visibility="collapsed",
            options=SUGGESTIONS.keys(),
            key="selected_suggestion",
        )

    st.button(
        "&nbsp;:small[:gray[:material/balance: Disclaimer]]",type="tertiary",on_click=show_disclaimer_dialog,
    )
    
    # Add disclaimer banner at the very bottom of start page
    st.markdown("---")
    st.markdown("""
<div style="text-align: center; padding: 10px; background-color: #f7f7f8; border-radius: 8px; margin: 10px 0;">
    <small style="color: #6b7280;">JereChat can make mistakes. Consider checking important information.</small>
</div>
""", unsafe_allow_html=True)
    
    st.stop()

# Show chat input at the bottom when a question has been asked.
user_message = st.chat_input("Ask a follow-up...")

if not user_message:
    if user_just_asked_initial_question:
        user_message = st.session_state.initial_question
    if user_just_clicked_suggestion:
        user_message = SUGGESTIONS[st.session_state.selected_suggestion]

with title_row:
    def clear_conversation():
        st.session_state.messages = []
        st.session_state.initial_question = None
        st.session_state.selected_suggestion = None
    
    st.button(
        "Restart",
        icon=":material/refresh:",
        on_click=clear_conversation,
    )

if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat messages from history as speech bubbles.
for i, message in enumerate(st.session_state.messages):
    render_history_message(i, message)

if user_message:
    # When the user posts a message...
    
    # Streamlit's Markdown engine interprets "$" as LaTeX code
    user_message = user_message.replace("$", r"\$")
    
    # Get random model order for this comparison
    left_model, right_model = ab_testing.get_model_order()
    
    # Display user message
    with st.chat_message("user"):
        st.text(user_message)
    
    # Generate responses from both models
    with st.spinner("Thinking..."):
        left_response, left_time = get_response(user_message, left_model)
        right_response, right_time = get_response(user_message, right_model)
        
        # Store response times
        st.session_state[f'response_times_{len(st.session_state.messages)}'] = {
            left_model: left_time,
            right_model: right_time
        }

    # Handle timeouts or errors by notifying user and preventing None rendering
    if left_response is None:
        st.error("Model request timed out.")
        left_response = ""
    if right_response is None:
        st.error("Model request timed out.")
        right_response = ""
    
    # Display side-by-side comparison (before reveal)
    render_comparison_message(
        index=len(st.session_state.messages) + 1,  # temporary index for UI before append
        left_model=left_model,
        right_model=right_model,
        left_response=left_response,
        right_response=right_response,
        show_buttons=False,
    )
    
    # Add to chat history
    st.session_state.messages.append({
        "role": "user",
        "content": user_message
    })
    st.session_state.messages.append({
        "role": "assistant",
        "model_order": (left_model, right_model),
        "left_response": left_response,
        "right_response": right_response
    })
    
    # Show preference buttons
    show_preference_buttons(len(st.session_state.messages) - 1, left_model, right_model)

# Add disclaimer banner at the very bottom
st.markdown("---")
st.markdown("""
<div style="text-align: center; padding: 10px; background-color: #f7f7f8; border-radius: 8px; margin: 10px 0;">
    <small style="color: #6b7280;">JereChat can make mistakes. Consider checking important information.</small>
</div>
""", unsafe_allow_html=True)