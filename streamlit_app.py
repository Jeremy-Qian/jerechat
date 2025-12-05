import streamlit as st
import datetime
import textwrap
from collections import namedtuple
import time
import jerechat as jc
from streamlit.runtime.scriptrunner import RerunException
from streamlit.runtime.scriptrunner import StopException

st.set_page_config(
    page_title="Streamlit AI assistant", 
    page_icon="✨",
    initial_sidebar_state="collapsed"
)

def check_invitation_code():
    """Check if user has entered a valid invitation code."""
    if 'invitation_verified' not in st.session_state:
        st.session_state.invitation_verified = False
    
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
            </style>
        """, unsafe_allow_html=True)
        
        # Create a form for the invitation code
        with st.form("invitation_form"):
            st.markdown("## 🔑 Enter Invitation Code")
            code = st.text_input("Please enter your 6-digit invitation code:", "", type="password")
            submitted = st.form_submit_button("Submit")
            
            if submitted:
                if code in valid_codes:
                    st.session_state.invitation_verified = True
                    st.rerun()
                else:
                    st.error("❌ Invalid invitation code. Please try again.")
        
        # Prevent the rest of the app from running
        st.stop()

# Check invitation code before showing the app
check_invitation_code()

# Initialize session state flags
if "generating" not in st.session_state:
    st.session_state.generating = False

# -----------------------------------------------------------------------------
# Sidebar with 'My Code' section
with st.sidebar:
    st.markdown("## My Code")
    st.markdown("""#### Great! You have an invitation code!""")

# -----------------------------------------------------------------------------
# Constants (keeping UI-related constants)
HISTORY_LENGTH = 5
DEBUG_MODE = st.query_params.get("debug", "false").lower() == "true"

CORTEX_URL = (
    "https://docs.snowflake.com/en/guides-overview-ai-features"
    "?utm_source=streamlit"
    "&utm_medium=referral"
    "&utm_campaign=streamlit-demo-apps"
    "&utm_content=streamlit-assistant"
)

GITHUB_URL = "https://github.com/streamlit/streamlit-assistant"

SUGGESTIONS = {
    ":blue[:material/local_library:] What is Streamlit?": (
        "What is Streamlit, what is it great at, and what can I do with it?"
    ),
    ":green[:material/database:] Help me understand session state": (
        "Help me understand session state. What is it for? "
        "What are gotchas? What are alternatives?"
    ),
    ":orange[:material/multiline_chart:] How do I make an interactive chart?": (
        "How do I make a chart where, when I click, another chart updates? "
        "Show me examples with Altair or Plotly."
    ),
    ":violet[:material/apparel:] How do I customize my app?": (
        "How do I customize my app? What does Streamlit offer? No hacks please."
    ),
    ":red[:material/deployed_code:] Deploying an app at work": (
        "How do I deploy an app at work? Give me easy and performant options."
    ),
}

# Helper objects
TaskInfo = namedtuple("TaskInfo", ["name", "function", "args"])
TaskResult = namedtuple("TaskResult", ["name", "result"])

# -----------------------------------------------------------------------------
# Simplified functions (without AI/Snowflake dependencies)

def build_question_prompt(question):
    """Direct question prompt - no extra context"""
    return question

def get_response(prompt):
    """Generate response using jerechat API"""
    try:
        if DEBUG_MODE:
            st.write(f"DEBUG: Calling jc.generate_response with prompt: {prompt[:50]}...")
        
        response_text = jc.generate_response(prompt, "1.5")
        
        if DEBUG_MODE:
            st.write(f"DEBUG: Got response: {response_text[:50]}...")
        
        # Yield chunks of ~20 characters to simulate line-by-line output
        chunk_size = 20
        for i in range(0, len(response_text), chunk_size):
            yield response_text[i:i + chunk_size]
            time.sleep(0.05)  # Reduced sleep time
    except Exception as e:
        if DEBUG_MODE:
            st.write(f"DEBUG: Exception in get_response: {str(e)}")
        st.error(f"Error generating response: {str(e)}")
        error_response = f"Sorry, I encountered an error: {str(e)}. Please try again."
        chunk_size = 20
        for i in range(0, len(error_response), chunk_size):
            yield error_response[i:i + chunk_size]
            time.sleep(0.05)  # Reduced sleep time

def send_telemetry(**kwargs):
    """Mock telemetry function"""
    pass

def show_feedback_controls(message_index):
    """Shows the "How did I do?" control."""
    st.write("")
    
    with st.popover("How did I do?"):
        with st.form(key=f"feedback-{message_index}", border=False):
            with st.container(gap=None):
                st.markdown(":small[Rating]")
                rating = st.feedback(options="stars")
            
            details = st.text_area("More information (optional)")
            
            if st.checkbox("Include chat history with my feedback", True):
                relevant_history = st.session_state.messages[:message_index]
            else:
                relevant_history = []
            
            ""  # Add some space
            
            if st.form_submit_button("Send feedback"):
                st.toast("Thank you for your feedback!")

@st.dialog("Legal disclaimer")
def show_disclaimer_dialog():
    st.caption("""
        This AI chatbot is a demo version. Answers may be inaccurate, inefficient, or biased.
        Any use or decisions based on such answers should include reasonable
        practices including human oversight to ensure they are safe,
        accurate, and suitable for your intended purpose. This is a demonstration
        application without AI capabilities.
    """)

# -----------------------------------------------------------------------------
# Draw the UI

st.markdown("""
<div style='font-size: 5rem; line-height: 1;'>❉</div>
""", unsafe_allow_html=True)

title_row = st.container(
    horizontal=True,
    vertical_alignment="bottom",
)

with title_row:
    st.title(
        "Streamlit AI assistant",
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
        st.chat_input("Ask a question...", key="initial_question", disabled=st.session_state.generating)
        
        selected_suggestion = st.pills(
            label="Examples",
            label_visibility="collapsed",
            options=SUGGESTIONS.keys(),
            key="selected_suggestion",
        )
    
    st.button(
        "&nbsp;:small[:gray[:material/balance: Legal disclaimer]]",
        type="tertiary",
        on_click=show_disclaimer_dialog,
    )
    
    st.stop()

# Show chat input at the bottom when a question has been asked.
user_message = st.chat_input("Ask a follow-up...", disabled=st.session_state.generating)

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
    with st.chat_message(message["role"]):
        if message["role"] == "assistant":
            st.container()  # Fix ghost message bug
        
        st.markdown(message["content"])
        
        if message["role"] == "assistant":
            show_feedback_controls(i)

if user_message and not st.session_state.generating:
    # When the user posts a message, store it and set generating flag
    st.session_state.pending_message = user_message
    st.session_state.generating = True
    st.rerun()

if st.session_state.generating and "pending_message" in st.session_state:
    try:
        # Process the pending message
        user_message = st.session_state.pending_message
        del st.session_state.pending_message
        
        # Streamlit's Markdown engine interprets "$" as LaTeX code
        user_message = user_message.replace("$", r"\$")
        
        # Display message as a speech bubble.
        with st.chat_message("user"):
            st.text(user_message)
        
        # Display assistant response as a speech bubble.
        with st.chat_message("assistant"):
            # Build a detailed prompt.
            if DEBUG_MODE:
                with st.status("Computing prompt...") as status:
                    full_prompt = build_question_prompt(user_message)
                    st.code(full_prompt)
                    status.update(label="Prompt computed")
            else:
                full_prompt = build_question_prompt(user_message)
            
            # Send prompt to echo function.
            with st.spinner("Thinking..."):
                time.sleep(1)
                response_gen = get_response(full_prompt)
            
            # Put everything after the spinners in a container to fix the
            # ghost message bug.
            with st.container():
                # Stream the response.
                response = st.write_stream(response_gen)
                
                # Add messages to chat history.
                st.session_state.messages.append({"role": "user", "content": user_message})
                st.session_state.messages.append({"role": "assistant", "content": response})
                
                # Other stuff.
                show_feedback_controls(len(st.session_state.messages) - 1)
                send_telemetry(question=user_message, response=response)
        
    except Exception as e:
        st.error(f"An error occurred while processing your message: {str(e)}")
        # Still add the user message to history so the conversation continues
        if "user_message" in locals():
            st.session_state.messages.append({"role": "user", "content": user_message})
            st.session_state.messages.append({"role": "assistant", "content": f"Sorry, I encountered an error: {str(e)}"})
    finally:
        # Always reset the generating flag
        st.session_state.generating = False
        st.rerun()