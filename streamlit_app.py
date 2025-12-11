import streamlit as st
import datetime
import textwrap
from collections import namedtuple
import time
import jerechat as jc
from streamlit.runtime.scriptrunner import RerunException
from streamlit.runtime.scriptrunner import StopException
from typing import Any, Dict, List, Optional
from supabase import Client, create_client

@st.dialog("Invitation Code Request")
def show_invitation_code_request():
    st.success("Your request has been submitted!")
    st.markdown("### Your free invitation code is:")
    # Get free invitation code from secrets instead of hardcoding
    free_code = st.secrets["freekey"]
    st.markdown(f"## :green[{free_code}]")
    st.info("You can use this code above to access JereChat.")

    # Add 'Go back' button to return to invitation code form
    if st.button("Back"):
        st.session_state.clear()
        st.rerun()  

@st.dialog("Free Key Disclaimer")
def show_freekey_disclaimer_dialog():
    st.caption("""
        Clicking the above button means that you acknowledge to the following:
        - You have read this disclaimer and fully understand;
        - You understand that your email data will be sent and stored to a remote SQL database;
        - You understand that the developer is not responsible for any damage or loss caused this website.
    """)


st.set_page_config(
    page_title="JereChat", 
    page_icon="✨",
    initial_sidebar_state="expanded"
)

def check_invitation_code():
    """Check if user has entered a valid and not expired invitation code."""
    if 'invitation_verified' not in st.session_state:
        st.session_state.invitation_verified = False
        st.session_state.active_code = None
    
    # Initialize session state for invitation request flow
    if 'show_invitation_request' not in st.session_state:
        st.session_state.show_invitation_request = False
    
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
            You can get access only by invitation codes. Check the sidebar for a free invitation code.", icon=":material/lock:")
        
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
        
        # Move 'Get an invitation code for free' functionality to sidebar
        with st.sidebar:
            if not st.session_state.show_invitation_request:
                # Add 'Get an invitation code for free' option
                st.markdown("## Don't have an invitation code?")
                if st.button("Get an invitation code for free", help="You get a free invitation code by using your gmail and password. Gmail Only.", type="primary"):
                    st.session_state.show_invitation_request = True
                    st.rerun()
                
                # Add disclaimer dialog
                st.button(
                    "&nbsp;:small[:gray[:material/balance: Disclaimer]]",
                    type="tertiary",
                    on_click=show_freekey_disclaimer_dialog,
                )
            
            else:
                # Show invitation code request form
                st.markdown("## Get Your Free Invitation Code")
                st.info("Enter your Gmail and password to receive a free invitation code.", icon=":material/info:")
                
                with st.form("invitation_request_form"):
                    gmail = st.text_input("Gmail Address:", type="default")
                    password = st.text_input("Password:", type="password")
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        submit_request = st.form_submit_button("Request Invitation Code")
                    with col2:
                        if st.form_submit_button("Go Back"):
                            st.session_state.show_invitation_request = False
                            st.rerun()
                
                if submit_request:
                    if not gmail or not password:
                        st.error("Please enter both Gmail and password.")
                    else:
                        # Save to Supabase - using local function instead of import
                        try:
                            def local_save_invitation_request(gmail: str, password: str) -> Optional[Dict[str, Any]]:
                                """
                                Save invitation code request to Supabase.
                                """
                                try:
                                    supabase_url = st.secrets.get("supabase_url")
                                    supabase_key = st.secrets.get("supabase_key")
                                    
                                    if not supabase_url or not supabase_key:
                                        st.error("Supabase credentials not configured.")
                                        return None
                                    
                                    supabase = create_client(supabase_url, supabase_key)
                                    data = {
                                        "gmail": gmail,
                                        "password": password,
                                        "created_at": datetime.datetime.now().isoformat()
                                    }
                                    result = supabase.table("invitation_requests").insert(data).execute()
                                    return result.data
                                except Exception as e:
                                    st.error(f"Failed to save invitation request: {e}")
                                    return None
                            
                            local_save_invitation_request(gmail, password)
                            show_invitation_code_request()
                            
                        except Exception as e:
                            st.error(f"Failed to submit request: {e}")
        
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
    ":blue[:material/door_open:] Knock Knock!": (
        "Play Knock Knock"
    ),
    ":green[:material/sentiment_very_satisfied:] Tell a joke": (
        "Tell a joke"
    ),
    ":orange[:material/draft:] Write an essay": (
        "Write an essay"
    ),
    ":violet[:material/code:] Write some code": (
        "Write some code"
    ),
    ":red[:material/skillet:] Cook JereChat": (
        "I'm gonna cook you"
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
        response_text = jc.generate_response(prompt, "1.5")
        # Handle multi-line responses with || separator
        response_text = response_text.replace("||", "  \n\n")
        # Yield chunks of ~30 characters to simulate line-by-line output
        chunk_size = 30
        for i in range(0, len(response_text), chunk_size):
            yield response_text[i:i + chunk_size]
            time.sleep(0.1)
    except Exception as e:
        error_response = f"Error: {str(e)}. Please rephrase."
        for i in range(0, len(error_response), chunk_size):
            yield error_response[i:i + chunk_size]
            time.sleep(0.1)

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
                relevant_history = st.session_state.messages[:message_index + 1]
            else:
                relevant_history = []
            
            ""  # Add some space
            
            if st.form_submit_button("Send feedback"):
                # Save feedback to Supabase
                feedback_type = "good" if rating and rating >= 3 else "bad"
                chat_history = relevant_history if 'relevant_history' in locals() and relevant_history else []
                try:
                    from database import save_feedback
                    save_feedback(message_index, feedback_type, chat_history, details=details)
                    st.toast("#####  Thank you for your feedback!", icon=":material/sentiment_very_satisfied:", duration="long")
                except Exception as e:
                    st.toast(f"Error saving feedback: {e}", icon=":material/error:")

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
        selected_model = st.pills(
            label="Models",
            label_visibility="collapsed",
            options=[
                ":material/neurology: DeepThink(Rampion 2)",
            ],
            key="selected_model",
            disabled=True,
        )

        
        selected_suggestion = st.pills(
            label="Examples",
            label_visibility="collapsed",
            options=SUGGESTIONS.keys(),
            key="selected_suggestion",
        )
    
    
    st.button(
        "&nbsp;:small[:gray[:material/balance: Disclaimer]]",type="tertiary",on_click=show_disclaimer_dialog,
    )
    
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
    with st.chat_message(message["role"]):
        if message["role"] == "assistant":
            st.container()  # Fix ghost message bug
        
        # Handle multi-line responses with || separator
        content = message["content"]
        if "||" in content and message["role"] == "assistant":
            content = content.replace("||", "  \n\n")
        st.markdown(content)
        
        if message["role"] == "assistant":
            show_feedback_controls(i)

if user_message:
    # When the user posts a message...
    
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