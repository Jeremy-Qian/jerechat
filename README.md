# 💬 Jerechat - Streamlit AI Assistant

A modern Streamlit chatbot application with invitation-based access, custom theming, and a sleek sidebar interface.

![Streamlit](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)

## ✨ Features

- **🔐 Invitation Code System**: Secure access control with 6-digit invitation codes
- **🎨 Custom Theme**: JetBrains Mono typography with light theme styling
- **💳 Interactive Sidebar**: Features a custom credit card HTML component with hover effects
- **🚫 Message Blocking**: Prevents new messages while generating responses
- **⏱️ Thinking Indicator**: 1-second thinking delay with spinner animation
- **📱 Responsive Design**: Works seamlessly across desktop and mobile devices

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- Streamlit

### Installation

1. **Clone the repository**
   ```bash
   git clone <your-repo-url>
   cd jerechat
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure invitation codes**
   
   Edit `.streamlit/secrets.toml` to add your invitation codes:
   ```toml
   invitation_codes = [
     "123456",
     "654321",
     "111222",
     "222333"
   ]
   ```

4. **Run the application**
   ```bash
   streamlit run streamlit_app.py
   ```

5. **Open your browser**
   
   Navigate to `http://localhost:8501` and enter one of your invitation codes to access the chat.

## 📁 Project Structure

```
jerechat/
├── streamlit_app.py          # Main application file
├── requirements.txt          # Python dependencies
├── README.md                 # This file
├── .streamlit/
│   ├── config.toml          # Streamlit theme configuration
│   └── secrets.toml         # Invitation codes and secrets
└── jerechat/                # Custom chat module
    └── ...
```

## 🎯 Usage

### Invitation Codes

- Users must enter a valid 6-digit invitation code to access the chat
- Codes are stored in `.streamlit/secrets.toml`
- The invitation dialog appears on first load

### Chat Interface

- **Message Blocking**: While the AI is generating a response, new messages are disabled
- **Thinking Phase**: Shows a 1-second "Thinking..." spinner before generating responses
- **Sidebar**: Displays the "My Code" section with a custom credit card component

### Customization

#### Theme
Edit `.streamlit/config.toml` to customize:
- Colors (background, text, primary)
- Typography (fonts, sizes, weights)
- Widget styling

#### Invitation Codes
Edit `.streamlit/secrets.toml` to:
- Add/remove invitation codes
- Store other application secrets

#### Sidebar Content
Modify the sidebar section in `streamlit_app.py`:
```python
with st.sidebar:
    st.markdown("## My Code")
    # Your custom HTML or components here
```

## 🛠️ Development

### Adding Features

1. **New Chat Functions**: Modify `get_response()` in `streamlit_app.py`
2. **UI Components**: Add to the main chat interface or sidebar
3. **Session State**: Use `st.session_state` for persistent data

### Debug Mode

Enable debug mode by adding `?debug=true` to the URL:
```
http://localhost:8501?debug=true
```

This shows:
- Prompt computation details
- Additional logging information

## 📋 Requirements

- streamlit
- jerechat (custom module)
- Python 3.8+

See `requirements.txt` for exact versions.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- Built with [Streamlit](https://streamlit.io/)
- Uses custom jerechat AI module
- Inspired by modern chat interface designs
