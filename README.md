# JereChat

A simple chatbot application built with Streamlit and Python, featuring invitation-based access control and feedback collection.

## Features

- **Corpus-based Q&A**: Uses Jaccard similarity matching to find the best response from a knowledge base
- **Invitation Code System**: Access control via expiring invitation codes
- **Feedback Collection**: User feedback stored in Supabase for improvement tracking
- **Custom Theming**: Modern UI with JetBrains Mono font and custom color scheme
- **Debug Mode**: Optional debug mode via query parameter for development

## Tech Stack

- [Streamlit](https://streamlit.io/) - Web application framework
- [Supabase](https://supabase.com/) - Backend database for feedback storage
- Python 3.x

## Getting Started

### Prerequisites

- Python 3.8 or later
- pip

### Installation

1. Clone the repository
```bash
git clone https://github.com/yourusername/jerechat.git
cd jerechat
```

2. Install dependencies
```bash
pip install -r requirements.txt
```

3. Set up Streamlit secrets

Create a `.streamlit/secrets.toml` file with the following structure:
```toml
supabase_url = "your-supabase-url"
supabase_key = "your-supabase-anon-key"

[[invitation_codes]]
code_number = "123456"
code_expiry_date = "2025-12-31"
code_notes = "Test invitation code"
```

4. Set up Supabase

Create a `feedback` table in your Supabase project with the following columns:
- `id` (int8, primary key)
- `created_at` (timestamptz)
- `message_index` (int4)
- `feedback_type` (text)
- `chat_history` (jsonb)
- `user_id` (text)

5. Run the application
```bash
streamlit run streamlit_app.py
```

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
└── README.md
```

## Customizing the Knowledge Base

Edit `jerechat/corpus.txt` to add or modify Q&A pairs:

- Questions start with a single `-`
- Answers start with `--`
- Multiple questions can map to the same answer
- Use `||` in answers for line breaks

Example:
```
-Hello
-Hi
-Hey
--Hi! How can I help you today?

-What is your name
--I'm JereChat, a simple chatbot.
```

## Debug Mode

Add `?debug=true` to the URL to enable debug mode, which shows the computed prompts.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.