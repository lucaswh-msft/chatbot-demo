# Chatbot MVP

A lightweight, extensible chatbot component built with React/TypeScript that integrates with FastAPI backends.

## Features

- 🚀 **Lightweight & Fast** - Minimal dependencies, optimized performance
- 🎨 **Customizable** - Themes, styling, and custom message renderers
- 🔄 **Streaming Support** - Real-time streaming responses
- 📱 **Responsive** - Works on desktop and mobile devices
- 🛠 **Extensible** - Plugin architecture and custom hooks
- 🔒 **Type Safe** - Full TypeScript support
- 🧪 **Testable** - Built with testing in mind

## Quick Start

### Frontend Setup

#### Installation

```bash
# Install frontend dependencies
npm install
```

#### Development

```bash
# Start React development server
npm start
```

The app will open at [http://localhost:3001](http://localhost:3001).

#### Build

```bash
# Build for production
npm run build
```

### Backend Setup

#### Installation

```bash
# Create and activate virtual environment
python -m venv .venv
.venv\Scripts\activate

# Install backend dependencies
pip install -r backend/requirements.txt
```

#### Development

```bash
# Start FastAPI development server
uvicorn backend.main:app --reload --port 8001
```

The API will be available at [http://localhost:8001](http://localhost:8001).

### Environment Configuration

Create a `.env` file in the root directory with the following settings:

```env
# Frontend Configuration
REACT_APP_CHAT_API_ENDPOINT=http://localhost:8001
REACT_APP_ENABLE_STREAMING=false
REACT_APP_MAX_MESSAGES=100
REACT_APP_USE_REAL_API=true
PORT=3001
```

Note: canonical ports used in this repository
- Frontend development server: http://localhost:3001 (set PORT=3001 in your .env)
- Backend API (uvicorn): http://localhost:8001 — start with:

```bash
uvicorn backend.main:app --reload --port 8001
```

## Usage

### Basic Usage

```tsx
import { ChatBot } from './components/chatbot';

function App() {
  return (
    <ChatBot
      apiEndpoint="http://localhost:8001/api/chat"
      theme="light"
      placeholder="Type your message..."
      height="600px"
    />
  );
}
```

### With Custom Configuration

```tsx
import { ChatBot } from './components/chatbot';

function App() {
  const handleMessageSent = (message: string) => {
    console.log('Message sent:', message);
  };

  const handleResponseReceived = (response: string) => {
    console.log('Response received:', response);
  };

  return (
    <ChatBot
      apiEndpoint="https://api.example.com/chat"
      apiKey="your-api-key"
      theme="dark"
      streamResponses={true}
      maxMessages={50}
      maxInputLength={2000}
      onMessageSent={handleMessageSent}
      onResponseReceived={handleResponseReceived}
      height="500px"
    />
  );
}
```

### Custom Message Renderer

```tsx
import { ChatBot, ChatMessageType } from './components/chatbot';
import ReactMarkdown from 'react-markdown';

const CustomRenderer = (message: ChatMessageType) => (
  <div className="custom-message">
    <ReactMarkdown>{message.content}</ReactMarkdown>
    <div className="metadata">
      {message.metadata?.tokens} tokens
    </div>
  </div>
);

function App() {
  return (
    <ChatBot
      apiEndpoint="http://localhost:8001/api/chat"
      customMessageRenderer={CustomRenderer}
    />
  );
}
```

## Configuration

### Environment Variables

Create a `.env` file in the root directory:

```env
# Chatbot Configuration
REACT_APP_CHAT_API_ENDPOINT=http://localhost:8001
REACT_APP_ENABLE_STREAMING=false
REACT_APP_MAX_MESSAGES=100
REACT_APP_ENABLE_ANALYTICS=false
REACT_APP_USE_REAL_API=true

# Development Settings
PORT=3001
GENERATE_SOURCEMAP=true
```

### Props

| Prop | Type | Default | Description |
|------|------|---------|-------------|
| `apiEndpoint` | `string` | **required** | Backend API endpoint |
| `apiKey` | `string` | `undefined` | API authentication key |
| `theme` | `'light' \| 'dark' \| 'auto'` | `'light'` | UI theme |
| `placeholder` | `string` | `'Type a message...'` | Input placeholder text |
| `maxMessages` | `number` | `100` | Maximum messages to keep in history |
| `streamResponses` | `boolean` | `false` | Enable streaming responses |
| `maxInputLength` | `number` | `4000` | Maximum input character length |
| `customMessageRenderer` | `function` | `undefined` | Custom message component renderer |
| `onMessageSent` | `function` | `undefined` | Callback when message is sent |
| `onResponseReceived` | `function` | `undefined` | Callback when response is received |
| `className` | `string` | `''` | Additional CSS classes |
| `height` | `string \| number` | `'600px'` | Container height |

## Architecture

### Project Structure

```
├── src/                             # Frontend source code
│   ├── components/
│   │   ├── chatbot/                 # Main chatbot components
│   │   │   ├── ChatBot.tsx          # Main container
│   │   │   ├── ChatMessage.tsx      # Message component
│   │   │   ├── ChatInput.tsx        # Input component
│   │   │   ├── ChatHistory.tsx      # Message history
│   │   │   ├── ChatHeader.tsx       # Header component
│   │   │   └── types.ts             # TypeScript interfaces
│   │   └── Demo.tsx                 # Demo component
│   ├── hooks/
│   │   ├── useChatBot.ts            # Main logic hook
│   │   ├── useChatMessages.ts       # Message state management
│   │   ├── useChatAPI.ts            # API integration
│   │   └── useChatStream.ts         # Streaming support
│   ├── services/
│   │   ├── chatAPI.ts               # API service layer
│   │   ├── mockAPI.ts               # Mock service for development
│   │   └── basaltAdapterAPI.ts      # Basalt API adapter service
│   ├── utils/
│   │   ├── messageFormatter.ts      # Message utilities
│   │   └── validation.ts            # Input validation
│   └── config/
│       └── chat.ts                  # Configuration settings
├── backend/                         # FastAPI backend
│   ├── main.py                      # Main FastAPI application
│   └── requirements.txt             # Python dependencies
├── public/                          # Static assets
└── build/                           # Production build output
```

### Data Flow

1. **User Input** → Input validation → Message creation
2. **API Call** → Backend integration → Response handling
3. **State Update** → Message history → UI re-render
4. **Streaming** → Real-time updates → Progressive rendering

### API Adapters

The chatbot supports multiple API integrations through adapter services:

#### Standard API

The default `chatAPI.ts` service handles communication with standard API endpoints following the schema defined in the Backend Integration section.

#### Mock API

The `mockAPI.ts` service provides simulated responses for development and testing. Enable it by setting `REACT_APP_USE_REAL_API=false`.

#### Basalt API Adapter

The `basaltAdapterAPI.ts` service translates between the chatbot's message format and the Basalt API format. It handles:

- Message format conversion
- Authentication
- Session management
- Simulated streaming for non-streaming APIs

To use the Basalt adapter:

```tsx
import { createBasaltAdapterService } from './services/basaltAdapterAPI';

const basaltService = createBasaltAdapterService({
  apiEndpoint: 'https://api.example.com',
  apiKey: 'your-api-key'
});

// Then pass to ChatBot component
<ChatBot apiService={basaltService} />
```

## Development

### Mock API

The app includes a mock API service for development. Set `REACT_APP_USE_REAL_API=false` to use mock responses.

### Testing

```bash
npm test
```

### Linting

```bash
npm run lint
```

## Backend Integration

The chatbot integrates with a FastAPI backend that provides the following endpoints:

### POST /services/conversation/web/api/v1/unified-chat/caip/init
Initialize a chat session.

**Request:**
```json
{
  "client": {
    "firstName": null,
    "lastName": null,
    "email": null,
    "phoneNumber": null,
    "memberships": { "isBetaMember": false, "isTotalTechSupport": false },
    "membershipList": [],
    "orderId": null
  },
  "id": "session_123",
  "message": {
    "requestedProductDataType": "drawer",
    "client": {
      "firstName": null,
      "lastName": null,
      "email": null,
      "phoneNumber": null,
      "memberships": { "isBetaMember": false, "isTotalTechSupport": false },
      "membershipList": [],
      "orderId": null
    }
  },
  "connection": "connecting",
  "provider": {
    "currentProvider": "caip",
    "queue": null,
    "previousProvider": null,
    "channel": "chat",
    "pillar": null,
    "category": null,
    "chatAttributes": null
  },
  "requestedAgentPool": "caip",
  "requestedAgentQueue": null,
  "clientId": "client_123",
  "caipConversationId": "conv_123",
  "paidMember": false,
  "loggedInAtInitChat": false,
  "isNative": true,
  "chatSessionStart": null,
  "mediaTrack": "text"
}
```

**Response:**
```json
{
  "status": "chat_initialized",
  "conversationId": "conv_123"
}
```

### POST /services/conversation/web/api/v1/unified-chat/caip/message
Send a message and get a response.

**Request:**
```json
{
  "client": {
    "firstName": null,
    "lastName": null,
    "email": null,
    "phoneNumber": null,
    "memberships": { "isBetaMember": false, "isTotalTechSupport": false },
    "membershipList": [],
    "orderId": ""
  },
  "id": "msg_123",
  "message": {
    "turnId": 1,
    "msgTimestamp": "2023-12-01T10:00:00Z",
    "latLong": null,
    "metadata": {
      "more": {
        "membershipState": "No",
        "logInState": "loggedOut",
        "referer": "web",
        "botSource": "dfcx",
        "requestedProductDataType": "drawer"
      },
      "correlationId": "corr_123",
      "conversationId": "conv_123",
      "genAI": true
    },
    "message": "Hello, how are you?",
    "msgSource": "user_typed"
  },
  "connection": "connected",
  "provider": {
    "currentProvider": "caip",
    "queue": null,
    "previousProvider": null,
    "channel": "chat",
    "pillar": null,
    "category": null,
    "chatAttributes": null
  },
  "requestedAgentPool": "caip",
  "requestedAgentQueue": null,
  "clientId": "client_123",
  "caipConversationId": "conv_123",
  "paidMember": false,
  "loggedInAtInitChat": false,
  "isNative": true,
  "chatSessionStart": null,
  "mediaTrack": "text"
}
```

**Response:**
```json
{
  "messages": [
    {
      "type": "Text",
      "displayText": "I'm doing well, thank you!",
      "hyperlinks": [],
      "options": []
    }
  ]
}
```

### LLM Backend (Azure OpenAI)

The backend can optionally use Azure OpenAI to generate assistant responses for the `/services/conversation/web/api/v1/unified-chat/caip/message` endpoint.

To enable the LLM integration, create a `backend/.env` file with the following variables (use your real key instead of the placeholder):

```env
AZURE_OPENAI_ENDPOINT=https://fde-prompt-evals.cognitiveservices.azure.com/
AZURE_OPENAI_KEY=<your-api-key>
AZURE_OPENAI_DEPLOYMENT=gpt-4.1-mini
AZURE_OPENAI_API_VERSION=2024-12-01-preview
```

Notes:

- The backend automatically loads `backend/.env` at startup using `python-dotenv`, so you do not need to export these vars manually when running the app via `uvicorn backend.main:app`.
- Make sure `python-dotenv` and `openai` are installed in the backend virtual environment (`backend/requirements.txt` includes these packages).
- If the LLM environment is not configured or a request to the model fails, the API will gracefully fall back to the original echo-style response (so the chatbot remains functional without the LLM).

### Streaming Support

The chatbot component supports streaming responses, but the backend API doesn't natively support streaming. The `basaltAdapterAPI.ts` service provides a compatibility layer that simulates streaming by chunking the full response.

### Chat History

The component supports chat history, but the current backend implementation doesn't persist messages. For production use, you would need to implement message storage and retrieval.

### Health Check

**GET /health**
Check if the API is running.

**Response:**
```json
{
  "status": "ok"
}
```

## Customization

### Themes

The component supports light and dark themes out of the box. You can customize colors by overriding CSS variables:

```css
.chatbot-container.custom-theme {
  --primary-color: #007acc;
  --secondary-color: #f5f5f5;
  --user-message-bg: #e3f2fd;
  --assistant-message-bg: #f9f9f9;
}
```

### Custom Styling

Add custom CSS classes:

```tsx
<ChatBot
  className="my-custom-chatbot"
  // ... other props
/>
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## License

MIT License - see LICENSE file for details.