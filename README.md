# JereChat - Usage Guide

JereChat is a simple, customizable chatbot application built with Streamlit and Python, featuring invitation-based access control and feedback collection. This guide will help you install, set up, and use JereChat effectively.

## Quick Start

### Installation
1. Clone the repository and install dependencies:
   ```bash
   git clone https://github.com/yourusername/jerechat.git
   cd jerechat
   pip install -r requirements.txt
   ```

2. Create a `.streamlit/secrets.toml` file with your Supabase credentials and invitation codes:
   ```toml
   supabase_url = "your-supabase-url"
   supabase_key = "your-supabase-anon-key"
   
   [[invitation_codes]]
   code_number = "123456"
   code_expiry_date = "2025-12-31"
   code_notes = "Test invitation code"
   ```

3. Run the application:
   ```bash
   streamlit run streamlit_app.py
   ```

4. Open your browser and navigate to the URL displayed in the terminal (typically `http://localhost:8501`)

## Accessing JereChat

### Invitation Code System
JereChat uses an invitation code system to control access. Each code has an expiry date and can be configured in the `.streamlit/secrets.toml` file.

### Using an Invitation Code
1. Launch JereChat by running the Streamlit application
2. On the welcome page, enter a valid invitation code in the input field
3. Click "Submit" to access the chat interface
4. If the code is valid and not expired, you'll be redirected to the chat page

## Using the Chat Interface

### Basic Chat Functionality
1. **Type your question** in the input field at the bottom of the chat window
2. **Press Enter or click "Send"** to submit your question
3. **Wait for a response** from JereChat
4. **Continue the conversation** by asking follow-up questions

### Interaction Examples
```
User: Hello
JereChat: Hi! How can I help you today?

User: What is your name?
JereChat: I'm JereChat, a simple chatbot.

User: How does this work?
JereChat: I use Jaccard similarity to match your questions with answers from my knowledge base.
```

### Understanding Responses
JereChat uses Jaccard similarity to find the best match for your question in its knowledge base. Here's how it works:
- The chatbot compares your question with all questions in its corpus
- It calculates the similarity between your question and each stored question
- It returns the answer associated with the most similar question

Responses are based solely on the information in the knowledge base. If your question doesn't match any stored questions closely enough, you may receive a generic response or no response.

## Customizing the Knowledge Base

The knowledge base is stored in `jerechat/corpus.txt` and contains Q&A pairs that the chatbot uses to generate responses.

### Q&A Format Rules
- **Questions** start with a single `-` character
- **Answers** start with `--` characters
- **Multiple questions** can map to the same answer (just list each question separately)
- **Line breaks** in answers: Use `||` to indicate a line break
- **Empty lines** separate different Q&A groups

### Example Corpus Entries
```
-Hello
-Hi
-Hey there
--Hi! How can I help you today?

-What is your name
-Who are you
--I'm JereChat, a simple chatbot built with Python and Streamlit.

-How do you work
-What's your matching algorithm
--I use Jaccard similarity to match your questions with answers in my knowledge base.||Jaccard similarity compares the words in your question with those in my stored questions to find the best match.
```

### Editing the Knowledge Base
1. Open `jerechat/corpus.txt` in a text editor
2. Add, modify, or delete Q&A pairs following the format rules
3. Save the file
4. Restart the Streamlit application to see your changes

## Advanced Features

### Debug Mode
Debug mode shows additional information about the matching process. To enable it:
1. Add `?debug=true` to the URL in your browser
2. Example: `http://localhost:8501/?debug=true`
3. Debug information includes:
   - All questions in the corpus
   - Similarity scores for each match
   - The final selected answer

### Feedback System
JereChat collects feedback on its responses. When you provide feedback:
1. It's stored in your Supabase database
2. Feedback includes the chat history and response quality
3. You can use this data to improve your knowledge base

### Customizing the Theme
To customize the visual theme:
1. Edit `.streamlit/config.toml`
2. Modify the theme settings (colors, font, etc.)
3. Save the file and refresh the application

## Troubleshooting

### Common Issues

#### Installation Issues
- **Problem**: `pip install -r requirements.txt` fails
  **Solution**: Ensure you're using Python 3.8 or later, and try upgrading pip: `pip install --upgrade pip`

#### Invitation Code Problems
- **Problem**: "Invalid or expired invitation code"
  **Solution**: Check that the code is entered correctly and hasn't passed its expiry date in `.streamlit/secrets.toml`

#### Chatbot Response Issues
- **Problem**: No response or irrelevant response
  **Solution**: Check your knowledge base for relevant Q&A pairs, and ensure your question is phrased clearly

#### Database Connection Errors
- **Problem**: "Connection to Supabase failed"
  **Solution**: Verify your Supabase URL and key in `.streamlit/secrets.toml`

## Supabase Setup

If you're setting up Supabase for the first time:

1. Create a new Supabase project
2. Add the following tables:
   - **feedback table**:
     - `id` (int8, primary key)
     - `created_at` (timestamptz)
     - `message_index` (int4)
     - `feedback_type` (text)
     - `chat_history` (jsonb)
     - `user_id` (text)

3. Copy your Supabase URL and anonymous key from the project settings
4. Paste them into your `.streamlit/secrets.toml` file

## Project Structure

```
jerechat/
├── .streamlit/
│   ├── config.toml      # Streamlit theme configuration
│   └── secrets.toml     # API keys and invitation codes (not in repo)
├── jerechat/
│   ├── __init__.py      # Core chatbot logic with Jaccard similarity
│   └── corpus.txt       # Q&A knowledge base
├── database.py          # Supabase integration for feedback
├── streamlit_app.py     # Main Streamlit application
├── requirements.txt     # Python dependencies
└── README.md            # This usage guide
```

## License

This project is licensed under the MIT License.