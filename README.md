# 🤖 Chat&Talk GPT - Your Personal AI Assistant

![Chat&Talk GPT](https://img.shields.io/badge/Version-1.0.0-purple)
![Python](https://img.shields.io/badge/Python-3.8+-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green)

A JARVIS-like personal AI assistant with voice interaction, multi-language support (English, Hindi, Nepali), and the ability to open apps and websites instantly.

## ✨ Features

### Core Features
- **🗣️ Voice Interaction**: Text-to-Speech (TTS) and Speech-to-Text (STT)
- **🌍 Multi-Language**: English, Hindi (हिंदी), and Nepali (नेपाली)
- **💬 ChatGPT-like Chat**: Natural conversation with AI
- **🎭 JARVIS Personality**: Calm, chill, and professional

### App/Website Opening
- **YouTube** - "Open YouTube"
- **WhatsApp** - "Open WhatsApp"
- **Chrome/Brave** - "Open Chrome"
- **VSCode** - "Open VSCode"
- **ChatGPT** - "Open ChatGPT"
- And many more!

### Visual Features
- **✨ 3D Particle Animation**: Alexa-style rotating nano-particle circle
- **🌈 Glowing AI Avatar**: Animated avatar with pulsing core
- **📱 Modern UI**: ChatGPT-inspired dark theme

## 🏗️ Project Structure

```
jarvis-ai/
├── backend/
│   ├── main.py              # FastAPI server (API routes)
│   ├── chat.py              # Chat history management
│   ├── model.py             # LLM integration (Groq/Ollama)
│   ├── tts.py               # Text-to-Speech
│   ├── stt.py               # Speech-to-Text
│   └── requirements.txt     # Python dependencies
│
├── frontend/
│   ├── index.html           # Main chat UI
│   ├── style.css            # Styling
│   └── script.js            # Frontend logic + 3D particles
│
├── config/
│   └── settings.json        # Configuration
│
├── memory/
│   └── chat_history.json    # Conversation history
│
└── .env                     # Environment variables (API keys)
```

## 🚀 Quick Start

### Prerequisites
- Python 3.8+ (for local development)
- Docker and Docker Compose (for containerized deployment)
- Web browser (Chrome/Firefox/Edge)
- Microphone (for voice features)

### Installation

1. **Clone or download this project**

2. **Choose your deployment method:**

   - [🐳 Docker Deployment](#-docker-deployment) (Recommended)
   - [💻 Local Development](#-local-development)

## 🐳 Docker Deployment (Recommended)

### Prerequisites
- [Docker](https://docs.docker.com/get-docker/) installed
- [Docker Compose](https://docs.docker.com/compose/install/) installed

### Quick Start

1. **Configure environment variables**
   ```bash
   # Copy the example environment file
   cp .env.docker .env
   ```
   
   Edit `.env` and add your API keys:
   ```env
   GROQ_API_KEY=your_groq_api_key_here
   # Add other optional API keys as needed
   ```

2. **Start services**
   ```bash
   # Development mode (with auto-reload)
   ./start-dev.sh
   
   # Production mode
   ./start-prod.sh
   ```

3. **Access the application**
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - API Documentation: http://localhost:8000/docs

### Docker Commands

| Command | Description |
|---------|-------------|
| `./start-dev.sh` | Start development environment |
| `./start-prod.sh` | Start production environment |
| `./stop.sh` | Stop all services |
| `docker-compose logs -f` | View logs |
| `docker-compose restart` | Restart services |
| `docker-compose down -v` | Stop and remove volumes |

### Environment Variables

Create a `.env` file with the following variables:

```env
# ============================================
# Required
# ============================================
GROQ_API_KEY=your_groq_api_key_here

# ============================================
# Optional: AI Providers
# ============================================
OPENAI_API_KEY=
ANTHROPIC_API_KEY=
GOOGLE_GENERATIVEAI_KEY=

# ============================================
# Optional: Email Notifications
# ============================================
SMTP_EMAIL=your_email@gmail.com
SMTP_PASSWORD=your_app_password
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
ADMIN_EMAIL=your_admin_email

# ============================================
# Optional: Google Sheets
# ============================================
GOOGLE_CREDENTIALS_JSON=
```

### Volumes

Data is persisted in Docker volumes:
- `db-data` - SQLite database
- `./memory` - Chat history and notes
- `./backend/voice_samples` - Generated voice files

### Customization

#### Building Custom Images
```bash
# Build backend only
docker-compose build backend

# Build frontend only
docker-compose build frontend

# Build without cache (production)
docker-compose build --no-cache
```

#### Running Individual Services
```bash
# Backend only
docker-compose up backend

# Frontend only
docker-compose up frontend
```

## 💻 Local Development

### Prerequisites
- Python 3.8+
- Web browser (Chrome/Firefox/Edge)
- Microphone (for voice features)

### Installation

1. **Clone or download this project**

2. **Install Python dependencies**
   ```bash
   cd backend
   pip install -r requirements.txt
   ```

3. **Configure API Key (Required)**
   
   Get a free API key from [Groq Console](https://console.groq.com/keys):
   ```bash
   # Edit .env file and add your API key
   GROQ_API_KEY=your_api_key_here
   ```

4. **Start the Server**
   ```bash
   cd backend
   python main.py
   ```

5. **Open in Browser**
   ```
   http://localhost:8000
   ```

## 🎯 Usage

### Chat Commands
- **General Chat**: Just type naturally!
- **Change Language**: "Reply in Hindi" or "नेपाली में बोलो"
- **Open Apps**: "Open YouTube", "Launch Chrome", "Start VSCode"

### Voice Commands
1. Click the microphone button and speak
2. Or type your message and press Enter

### Settings
- Click the gear icon to change:
  - Voice (Male/Female)
  - Language preference
  - Enable/disable voice features

## 📡 API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Serve frontend |
| `/api/chat` | POST | Send chat message |
| `/api/tts` | POST | Text-to-speech |
| `/api/stt` | POST | Speech-to-text |
| `/api/config` | GET | Get settings |
| `/ws/chat` | WebSocket | Real-time chat |

## 🔧 Configuration

### Environment Variables (.env)
```env
# Groq API (Free)
GROQ_API_KEY=your_key_here

# Optional: Ollama (Local LLM)
OLLAMA_URL=http://localhost:11434
OLLAMA_MODEL=llama3.2

# Server
HOST=0.0.0.0
PORT=8000
```

### settings.json
Edit `config/settings.json` to customize:
- Assistant name and personality
- Default voice and language
- App/URL mappings
- UI theme

## 🐛 Debugging

The application includes logging for troubleshooting:

```python
# Check console output for:
# - API calls and responses
# - TTS/STT status
# - Connection errors
```

### Common Issues

1. **No response from AI**
   - Check your Groq API key in `.env`
   - Verify internet connection

2. **Voice not working**
   - Check microphone permissions
   - Try different browser (Chrome recommended)

3. **Apps won't open**
   - Browser security blocks some app launches
   - Use URL-based apps (YouTube, WhatsApp Web) instead

## 📝 License

MIT License - Feel free to modify and use!

## 🙏 Acknowledgments

- [Groq](https://groq.com) - Free LLM API
- [Three.js](https://threejs.org) - 3D particles
- [Edge-TTS](https://github.com/rany2/edge-tts) - Text-to-Speech
- [Ollama](https://ollama.com) - Local LLM (optional)

---

Made with ❤️ as your personal AI assistant!
