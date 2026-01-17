# ANAY - Advanced Neural AI sYstem

A fully functional, intelligent personal AI assistant with React frontend and Python backend, featuring voice interaction, system control, and real-time animations.

## Features

- 🎤 **Voice Interaction**: Speech-to-text and text-to-speech with Hindi language support
- 🤖 **AI Intelligence**: Powered by Google Gemini API with contextual memory
- 🎨 **Beautiful UI**: Futuristic design with particle-based animations that react to audio
- 💻 **System Control**: Cross-platform file/app operations and Spotify control
- 🔄 **Real-time Communication**: WebSocket-based bidirectional communication
- 🌐 **Cross-platform**: Works on Windows, macOS, and Linux

## Architecture

- **Frontend**: React + TypeScript + Vite + Three.js + Framer Motion
- **Backend**: Python FastAPI + WebSocket + Gemini API
- **Communication**: WebSocket for real-time, HTTP for health checks

## Setup Instructions

### Backend Setup

1. Navigate to the backend directory:
```bash
cd backend
```

2. Create a virtual environment (recommended):
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create `.env` file:
```bash
cp .env.example .env
```

5. Add your Gemini API key to `.env`:
```
GEMINI_API_KEY=your_api_key_here
```

6. Run the backend server:
```bash
python main.py
```

The backend will start on `http://localhost:8000`

### Frontend Setup

1. Navigate to the frontend directory:
```bash
cd anay-your-ai-companion
```

2. Install dependencies:
```bash
npm install
```

3. Create `.env` file (optional, defaults are set):
```bash
VITE_API_URL=http://localhost:8000
VITE_WS_URL=ws://localhost:8000/ws
```

4. Run the development server:
```bash
npm run dev
```

The frontend will start on `http://localhost:8080`

## Usage

1. Start the backend server first
2. Start the frontend development server
3. Open `http://localhost:8080` in your browser (Chrome recommended for best speech recognition)
4. Click the microphone button to start voice interaction
5. Speak in Hindi or English - ANAY will respond in Hindi

## System Control Commands

ANAY can perform system-level tasks:

- **Open Files**: "file खोलो [path]" or "open file [path]"
- **Open Folders**: "folder खोलो [path]" or "open folder [path]"
- **Launch Apps**: "app खोलो [name]" or "launch [app name]"
- **Spotify Control**: "Spotify पर गाना बजाओ [song]" or "play music [song]"

## Project Structure

```
.
├── backend/                 # Python FastAPI backend
│   ├── main.py             # FastAPI app and WebSocket server
│   ├── ai_brain.py         # Gemini API integration
│   ├── memory.py           # Conversation memory management
│   ├── system_control.py   # Cross-platform system operations
│   ├── config.py           # Configuration
│   └── requirements.txt    # Python dependencies
│
└── anay-your-ai-companion/ # React frontend
    ├── src/
    │   ├── components/     # UI components
    │   ├── hooks/          # React hooks (chat, speech)
    │   ├── lib/            # WebSocket and API clients
    │   └── pages/          # Page components
    └── package.json        # Frontend dependencies
```

## Development

### Backend Development

- Backend uses FastAPI with auto-reload enabled
- WebSocket endpoint: `/ws`
- Health check: `/health`

### Frontend Development

- Uses Vite for fast HMR
- TypeScript for type safety
- Tailwind CSS for styling

## Troubleshooting

### WebSocket Connection Issues

- Ensure backend is running on port 8000
- Check CORS settings in `backend/config.py`
- Verify WebSocket URL in frontend `.env`

### Speech Recognition Not Working

- Use Chrome browser for best compatibility
- Grant microphone permissions
- Check browser console for errors

### Gemini API Errors

- Verify API key in `backend/.env`
- Check API quota/limits
- Review backend logs for detailed errors

## Security Notes

- Never commit `.env` files with API keys
- System control operations are permission-based
- File paths are validated before execution
- WebSocket connections should use WSS in production

## License

MIT License

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
