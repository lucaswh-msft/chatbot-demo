# Chatbot MVP Usage Guide

## 🚀 Quick Start

### 1. Installation & Setup

```bash
# Install dependencies
npm install

# Start development server
npm start
```

The application will open at [http://localhost:3001](http://localhost:3001).

### 2. Basic Integration

```tsx
import { ChatBot } from './components/chatbot';

function MyApp() {
  return (
    <ChatBot
      apiEndpoint="https://your-api.com/chat"
      theme="light"
      height="600px"
    />
  );
}
```

## 🎛️ Configuration Options

### Core Props

| Prop | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| `apiEndpoint` | `string` | ✅ | - | Backend API endpoint |
| `apiKey` | `string` | ❌ | - | API authentication key |
| `theme` | `'light' \| 'dark'` | ❌ | `'light'` | UI theme |
| `height` | `string \| number` | ❌ | `'600px'` | Container height |

### Behavior Props

| Prop | Type | Default | Description |
|------|------|---------|-------------|
| `streamResponses` | `boolean` | `false` | Enable real-time streaming |
| `maxMessages` | `number` | `100` | Max messages in history |
| `maxInputLength` | `number` | `4000` | Max input characters |
| `placeholder` | `string` | `'Type a message...'` | Input placeholder |

### Callback Props

| Prop | Type | Description |
|------|------|-------------|
| `onMessageSent` | `(message: string) => void` | Called when user sends message |
| `onResponseReceived` | `(response: string) => void` | Called when AI responds |
| `customMessageRenderer` | `(message: ChatMessage) => ReactNode` | Custom message component |

## 🎨 Customization Examples

### 1. Dark Theme with Streaming

```tsx
<ChatBot
  apiEndpoint="https://api.example.com/chat"
  theme="dark"
  streamResponses={true}
  maxMessages={50}
  placeholder="Ask me anything..."
  height="500px"
/>
```

### 2. Custom Message Renderer

```tsx
import ReactMarkdown from 'react-markdown';

const MarkdownRenderer = (message: ChatMessage) => (
  <div className="markdown-message">
    <ReactMarkdown>{message.content}</ReactMarkdown>
    {message.metadata?.tokens && (
      <small>{message.metadata.tokens} tokens</small>
    )}
  </div>
);

<ChatBot
  apiEndpoint="https://api.example.com/chat"
  customMessageRenderer={MarkdownRenderer}
/>
```

### 3. Event Handling

```tsx
const handleMessageSent = (message: string) => {
  console.log('User said:', message);
  // Track analytics, log to server, etc.
};

const handleResponseReceived = (response: string) => {
  console.log('AI responded:', response);
  // Process response, trigger actions, etc.
};

<ChatBot
  apiEndpoint="https://api.example.com/chat"
  onMessageSent={handleMessageSent}
  onResponseReceived={handleResponseReceived}
/>
```

## 🔧 Development Mode

### Mock API

The chatbot includes a mock API for development. Configure via environment variables:

```env
# .env
REACT_APP_USE_REAL_API=false  # Use mock responses
REACT_APP_ENABLE_STREAMING=true
REACT_APP_MAX_MESSAGES=100
```

### Debug Features

- Mock responses with realistic delays
- Error simulation (5% chance)
- Streaming simulation
- Console logging for all events

## 🏗️ Backend Integration

### Expected API Endpoints

#### POST /chat/messages
Send a message and receive response.

**Request:**
```json
{
  "content": "Hello, how are you?",
  "session_id": "optional-session-id"
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

#### POST /chat/stream (Optional)
Stream responses in real-time using Server-Sent Events.

#### GET /chat/messages/{session_id} (Optional)
Retrieve chat history for session persistence.

## 🎯 Use Cases

### 1. Customer Support Widget

```tsx
<ChatBot
  apiEndpoint="/api/support-chat"
  theme="light"
  placeholder="How can we help you today?"
  maxInputLength={2000}
  className="support-widget"
  height="400px"
/>
```

### 2. AI Assistant Dashboard

```tsx
<ChatBot
  apiEndpoint="/api/ai-assistant"
  theme="dark"
  streamResponses={true}
  maxMessages={200}
  placeholder="Ask your AI assistant..."
  height="100vh"
/>
```

### 3. Educational Chatbot

```tsx
<ChatBot
  apiEndpoint="/api/tutor-chat"
  theme="light"
  customMessageRenderer={EducationalRenderer}
  onMessageSent={trackLearningProgress}
  placeholder="What would you like to learn?"
/>
```

## 🧪 Testing

### Run Tests

```bash
npm test
```

### Test Coverage

The MVP includes tests for:
- Component rendering
- User interactions
- Message sending/receiving
- Theme switching
- Error handling
- Callback execution

### Manual Testing Checklist

- [ ] Send and receive messages
- [ ] Switch between light/dark themes
- [ ] Test with long messages (near character limit)
- [ ] Test error scenarios (network issues)
- [ ] Test streaming responses (if enabled)
- [ ] Test responsive design on mobile
- [ ] Test keyboard shortcuts (Enter to send)
- [ ] Test clear chat functionality

## 🚀 Deployment

### Build for Production

```bash
npm run build
```

### Environment Configuration

```env
# Production .env
REACT_APP_CHAT_API_ENDPOINT=https://your-production-api.com/chat
REACT_APP_USE_REAL_API=true
REACT_APP_ENABLE_STREAMING=true
REACT_APP_MAX_MESSAGES=100
```

### Docker Deployment (Optional)

```dockerfile
FROM node:18-alpine
WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production
COPY . .
RUN npm run build
EXPOSE 3001
CMD ["npm", "start"]
```

## 🔍 Troubleshooting

### Common Issues

1. **Messages not sending**
   - Check API endpoint configuration
   - Verify network connectivity
   - Check browser console for errors

2. **Styling issues**
   - Ensure CSS is properly imported
   - Check for conflicting styles
   - Verify theme prop is set correctly

3. **Performance issues**
   - Reduce `maxMessages` for large histories
   - Consider implementing message virtualization
   - Check for memory leaks in custom renderers

### Debug Tools

- Browser DevTools Console
- Network tab for API calls
- React DevTools for component state
- Performance tab for optimization

## 📚 API Reference

### Hooks

- `useChatBot(config)` - Main chatbot logic
- `useChatMessages(maxMessages)` - Message state management
- `useChatAPI(config)` - API integration
- `useChatStream(config)` - Streaming support

### Utilities

- `createUserMessage(content)` - Create user message object
- `createAssistantMessage(content, metadata)` - Create assistant message
- `validateMessage(content, maxLength)` - Input validation
- `formatTimestamp(date)` - Format message timestamps

### Types

- `ChatMessage` - Message interface
- `ChatBotConfig` - Configuration interface
- `ChatBotProps` - Component props interface
- `ChatMessageRequest` - API request interface
- `ChatMessageResponse` - API response interface

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/new-feature`
3. Make changes and add tests
4. Run tests: `npm test`
5. Build: `npm run build`
6. Submit a pull request

## 📄 License

MIT License - see LICENSE file for details.