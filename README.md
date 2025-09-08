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

### Installation

```bash
npm install
```

### Development

```bash
npm start
```

The app will open at [http://localhost:3001](http://localhost:3001).

### Build

```bash
npm run build
```

## Usage

### Basic Usage

```tsx
import { ChatBot } from './components/chatbot';

function App() {
  return (
    <ChatBot
      apiEndpoint="http://localhost:8000/api/chat"
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
      apiEndpoint="http://localhost:8000/api/chat"
      customMessageRenderer={CustomRenderer}
    />
  );
}
```

## Configuration

### Environment Variables

Create a `.env` file in the root directory:

```env
REACT_APP_CHAT_API_ENDPOINT=http://localhost:8000/api/chat
REACT_APP_ENABLE_STREAMING=false
REACT_APP_MAX_MESSAGES=100
REACT_APP_USE_REAL_API=false
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

### Component Structure

```
src/
├── components/
│   └── chatbot/
│       ├── ChatBot.tsx              # Main container
│       ├── ChatMessage.tsx          # Message component
│       ├── ChatInput.tsx            # Input component
│       ├── ChatHistory.tsx          # Message history
│       ├── ChatHeader.tsx           # Header component
│       └── types.ts                 # TypeScript interfaces
├── hooks/
│   ├── useChatBot.ts                # Main logic hook
│   ├── useChatMessages.ts           # Message state management
│   ├── useChatAPI.ts                # API integration
│   └── useChatStream.ts             # Streaming support
├── services/
│   ├── chatAPI.ts                   # API service layer
│   └── mockAPI.ts                   # Mock service for development
└── utils/
    ├── messageFormatter.ts          # Message utilities
    └── validation.ts                # Input validation
```

### Data Flow

1. **User Input** → Input validation → Message creation
2. **API Call** → Backend integration → Response handling
3. **State Update** → Message history → UI re-render
4. **Streaming** → Real-time updates → Progressive rendering

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

The chatbot expects a FastAPI backend with the following endpoints:

### POST /chat/messages
Send a message and get a response.

**Request:**
```json
{
  "content": "Hello, how are you?",
  "session_id": "optional-session-id",
  "context": {}
}
```

**Response:**
```json
{
  "id": "msg_123",
  "content": "I'm doing well, thank you!",
  "role": "assistant",
  "timestamp": "2023-12-01T10:00:00Z",
  "metadata": {
    "tokens": 25,
    "model": "gpt-3.5-turbo"
  }
}
```

### POST /chat/stream
Stream a response in real-time.

**Request:** Same as above

**Response:** Server-Sent Events stream with JSON chunks

### GET /chat/messages/{session_id}
Retrieve chat history for a session.

**Response:**
```json
[
  {
    "id": "msg_123",
    "content": "Hello",
    "role": "user",
    "timestamp": "2023-12-01T10:00:00Z",
    "session_id": "session_123"
  }
]
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