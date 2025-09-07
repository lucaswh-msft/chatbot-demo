# Chatbot Component Architecture Design

## Overview

This document outlines the architecture for a lightweight, extensible chatbot component built with React/TypeScript that integrates with our FastAPI backend. The design prioritizes simplicity while maintaining completeness and extensibility for various customer deployments.

## Core Architecture

### Frontend Component Structure

```
src/
├── components/
│   ├── chatbot/
│   │   ├── ChatBot.tsx              # Main chatbot container
│   │   ├── ChatMessage.tsx          # Individual message component
│   │   ├── ChatInput.tsx            # Message input with send button
│   │   ├── ChatHistory.tsx          # Scrollable message history
│   │   ├── ChatHeader.tsx           # Optional header with title/status
│   │   └── types.ts                 # TypeScript interfaces
│   └── ui/                          # shadcn/ui components
├── hooks/
│   ├── useChatBot.ts                # Main chatbot logic hook
│   ├── useChatMessages.ts           # Message state management
│   └── useChatStream.ts             # Streaming response handling
├── services/
│   └── chatAPI.ts                   # API service layer
└── utils/
    ├── messageFormatter.ts          # Message formatting utilities
    └── validation.ts                # Input validation with zod
```

### Component API Design

#### Main ChatBot Component

```typescript
interface ChatBotProps {
  // Core configuration
  apiEndpoint: string;
  apiKey?: string;
  
  // Customization
  theme?: 'light' | 'dark' | 'auto';
  placeholder?: string;
  maxMessages?: number;
  
  // Behavior
  streamResponses?: boolean;
  allowFileUpload?: boolean;
  maxInputLength?: number;
  
  // Extensibility
  customMessageRenderer?: (message: ChatMessage) => ReactNode;
  onMessageSent?: (message: string) => void;
  onResponseReceived?: (response: string) => void;
  
  // Styling
  className?: string;
  height?: string | number;
}
```

#### Message Interface

```typescript
interface ChatMessage {
  id: string;
  content: string;
  role: 'user' | 'assistant' | 'system';
  timestamp: Date;
  metadata?: {
    tokens?: number;
    model?: string;
    error?: boolean;
    streaming?: boolean;
  };
}
```

## Backend Integration

### FastAPI Endpoint Structure

```python
# routes/chat.py
@router.post("/chat/messages")
async def send_message(
    message: ChatMessageRequest,
    session_id: Optional[str] = None
) -> ChatMessageResponse:
    """Send a message and get AI response"""
    pass

@router.get("/chat/messages/{session_id}")
async def get_chat_history(
    session_id: str,
    limit: int = 50
) -> List[ChatMessage]:
    """Retrieve chat history for a session"""
    pass

@router.post("/chat/stream")
async def stream_message(
    message: ChatMessageRequest,
    session_id: Optional[str] = None
) -> StreamingResponse:
    """Stream AI response in real-time"""
    pass
```

### Pydantic Models

```python
class ChatMessageRequest(BaseModel):
    content: str = Field(..., max_length=4000)
    session_id: Optional[str] = None
    context: Optional[Dict[str, Any]] = None

class ChatMessageResponse(BaseModel):
    id: str
    content: str
    role: Literal["assistant"]
    timestamp: datetime
    metadata: Optional[Dict[str, Any]] = None

class ChatMessage(BaseModel):
    id: str
    content: str
    role: Literal["user", "assistant", "system"]
    timestamp: datetime
    session_id: str
    metadata: Optional[Dict[str, Any]] = None
```

## State Management

### Custom Hooks Pattern

```typescript
// useChatBot.ts - Main orchestration hook
export const useChatBot = (config: ChatBotConfig) => {
  const { messages, addMessage, updateMessage } = useChatMessages();
  const { sendMessage, isLoading } = useChatAPI(config);
  const { startStream, stopStream } = useChatStream(config);

  const handleSendMessage = useCallback(async (content: string) => {
    const userMessage = createUserMessage(content);
    addMessage(userMessage);
    
    if (config.streamResponses) {
      await startStream(content, userMessage.id);
    } else {
      await sendMessage(content);
    }
  }, [config, addMessage, sendMessage, startStream]);

  return {
    messages,
    sendMessage: handleSendMessage,
    isLoading,
    // ... other exposed methods
  };
};
```

## Data Flow

### Non-Streaming Flow
```
User Input → Validation → API Call → Response → UI Update
     ↓
[ChatInput] → [useChatBot] → [chatAPI] → [FastAPI] → [Azure AI]
     ↓
[ChatHistory] ← [State Update] ← [Response] ← [JSON] ← [AI Response]
```

### Streaming Flow
```
User Input → WebSocket/SSE → Streaming Response → Real-time UI Updates
     ↓
[ChatInput] → [useChatStream] → [FastAPI Stream] → [Azure AI Stream]
     ↓
[ChatHistory] ← [Incremental Updates] ← [Stream Chunks] ← [Token Stream]
```

## Extensibility Points

### 1. Custom Message Renderers
```typescript
const CustomMarkdownRenderer = (message: ChatMessage) => (
  <div className="custom-message">
    <ReactMarkdown>{message.content}</ReactMarkdown>
    <div className="message-metadata">
      {message.metadata?.tokens} tokens
    </div>
  </div>
);

<ChatBot 
  customMessageRenderer={CustomMarkdownRenderer}
  // ... other props
/>
```

### 2. Plugin Architecture
```typescript
interface ChatBotPlugin {
  name: string;
  onMessageSent?: (message: string) => void;
  onResponseReceived?: (response: string) => void;
  customCommands?: Record<string, (args: string[]) => void>;
}

const plugins: ChatBotPlugin[] = [
  {
    name: 'analytics',
    onMessageSent: (message) => analytics.track('chat_message_sent'),
    onResponseReceived: (response) => analytics.track('chat_response_received')
  }
];
```

### 3. Theme Customization
```typescript
const customTheme = {
  primary: '#007acc',
  secondary: '#f5f5f5',
  messageBackground: {
    user: '#e3f2fd',
    assistant: '#f9f9f9'
  }
};

<ChatBot theme={customTheme} />
```

## Deployment Configuration

### Environment Variables
```typescript
// config/chat.ts
export const chatConfig = {
  apiEndpoint: process.env.REACT_APP_CHAT_API_ENDPOINT || '/api/chat',
  enableStreaming: process.env.REACT_APP_ENABLE_STREAMING === 'true',
  maxMessages: parseInt(process.env.REACT_APP_MAX_MESSAGES || '100'),
  enableAnalytics: process.env.REACT_APP_ENABLE_ANALYTICS === 'true'
};
```

### Customer-Specific Configurations
```typescript
// config/customers/customer1.ts
export const customer1Config: ChatBotConfig = {
  theme: 'corporate-blue',
  maxInputLength: 2000,
  enableFileUpload: false,
  customPrompt: "You are a helpful assistant for Customer 1..."
};
```

## Testing Strategy

### Unit Tests
```typescript
// __tests__/useChatBot.test.ts
describe('useChatBot', () => {
  it('should add user message when sending', async () => {
    const { result } = renderHook(() => useChatBot(mockConfig));
    
    await act(async () => {
      await result.current.sendMessage('Hello');
    });
    
    expect(result.current.messages).toHaveLength(1);
    expect(result.current.messages[0].role).toBe('user');
  });
});
```

### Integration Tests
```typescript
// __tests__/ChatBot.integration.test.ts
describe('ChatBot Integration', () => {
  it('should handle full conversation flow', async () => {
    render(<ChatBot {...testProps} />);
    
    const input = screen.getByPlaceholderText('Type a message...');
    const sendButton = screen.getByRole('button', { name: /send/i });
    
    fireEvent.change(input, { target: { value: 'Hello' } });
    fireEvent.click(sendButton);
    
    await waitFor(() => {
      expect(screen.getByText('Hello')).toBeInTheDocument();
    });
  });
});
```

## Error Handling

### Frontend Error Boundaries
```typescript
class ChatBotErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false, error: null };
  }

  static getDerivedStateFromError(error) {
    return { hasError: true, error };
  }

  render() {
    if (this.state.hasError) {
      return (
        <div className="chat-error">
          <h3>Something went wrong</h3>
          <button onClick={() => this.setState({ hasError: false })}>
            Retry
          </button>
        </div>
      );
    }
    return this.props.children;
  }
}
```

### API Error Handling
```typescript
const useChatAPI = (config: ChatBotConfig) => {
  const [error, setError] = useState<string | null>(null);
  
  const sendMessage = async (content: string) => {
    try {
      setError(null);
      const response = await fetch(`${config.apiEndpoint}/messages`, {
        method: 'POST',
        body: JSON.stringify({ content }),
        headers: { 'Content-Type': 'application/json' }
      });
      
      if (!response.ok) {
        throw new Error(`API Error: ${response.status}`);
      }
      
      return await response.json();
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Unknown error';
      setError(errorMessage);
      throw err;
    }
  };
  
  return { sendMessage, error };
};
```

## Performance Considerations

### Message Virtualization
For large chat histories, implement virtualization to maintain performance:

```typescript
import { FixedSizeList as List } from 'react-window';

const ChatHistory = ({ messages }: { messages: ChatMessage[] }) => (
  <List
    height={400}
    itemCount={messages.length}
    itemSize={100}
    itemData={messages}
  >
    {({ index, data, style }) => (
      <div style={style}>
        <ChatMessage message={data[index]} />
      </div>
    )}
  </List>
);
```

### Message Debouncing
```typescript
const useDebouncedInput = (delay: number = 300) => {
  const [input, setInput] = useState('');
  const [debouncedInput, setDebouncedInput] = useState('');

  useEffect(() => {
    const timer = setTimeout(() => setDebouncedInput(input), delay);
    return () => clearTimeout(timer);
  }, [input, delay]);

  return [debouncedInput, setInput] as const;
};
```

## Developer Debug View

### Debug Panel Architecture

The debug view provides comprehensive insights into chatbot behavior, API calls, and internal state for development and troubleshooting.

```
src/
├── components/
│   ├── chatbot/
│   │   └── debug/
│   │       ├── DebugPanel.tsx           # Main debug container
│   │       ├── MessageDebugView.tsx     # Individual message inspection
│   │       ├── APICallsPanel.tsx        # Network requests log
│   │       ├── StateInspector.tsx       # React state visualization
│   │       ├── PromptViewer.tsx         # JSX prompt inspection
│   │       ├── PerformancePanel.tsx     # Timing and metrics
│   │       └── ConfigPanel.tsx          # Live configuration editing
├── hooks/
│   ├── useDebugMode.ts                  # Debug mode state management
│   ├── useAPILogger.ts                  # Network call interceptor
│   └── usePerformanceMetrics.ts         # Performance tracking
└── utils/
    ├── debugHelpers.ts                  # Debug utility functions
    └── devTools.ts                      # Browser dev tools integration
```

### Debug Mode Activation

```typescript
// Debug mode controlled by environment variable and URL parameter
const useDebugMode = () => {
  const [isDebugMode, setIsDebugMode] = useState(() => {
    const isDev = process.env.NODE_ENV === 'development';
    const hasDebugParam = new URLSearchParams(window.location.search).has('debug');
    const hasDebugStorage = localStorage.getItem('fde-chatbot-debug') === 'true';
    
    return isDev && (hasDebugParam || hasDebugStorage);
  });

  const toggleDebug = useCallback(() => {
    const newState = !isDebugMode;
    setIsDebugMode(newState);
    localStorage.setItem('fde-chatbot-debug', newState.toString());
  }, [isDebugMode]);

  return { isDebugMode, toggleDebug };
};
```

### Enhanced ChatBot Component with Debug Support

```typescript
interface ChatBotProps {
  // ... existing props
  
  // Debug-specific props
  enableDebug?: boolean;
  debugPosition?: 'right' | 'bottom' | 'floating';
  debugDefaultOpen?: boolean;
}

const ChatBot: React.FC<ChatBotProps> = (props) => {
  const { isDebugMode } = useDebugMode();
  const debugData = useDebugData();
  
  return (
    <div className="chatbot-container">
      <div className="chatbot-main">
        {/* Main chatbot components */}
      </div>
      
      {(isDebugMode || props.enableDebug) && (
        <DebugPanel 
          data={debugData}
          position={props.debugPosition}
          defaultOpen={props.debugDefaultOpen}
        />
      )}
    </div>
  );
};
```

### Debug Data Collection Hook

```typescript
interface DebugData {
  messages: ChatMessage[];
  apiCalls: APICallLog[];
  state: ChatBotState;
  performance: PerformanceMetrics;
  prompts: PromptDebugInfo[];
  config: ChatBotConfig;
  errors: ErrorLog[];
}

const useDebugData = (): DebugData => {
  const apiLogger = useAPILogger();
  const performanceMetrics = usePerformanceMetrics();
  const [errors, setErrors] = useState<ErrorLog[]>([]);
  
  // Collect and aggregate all debug information
  return {
    messages: chatMessages,
    apiCalls: apiLogger.calls,
    state: chatBotState,
    performance: performanceMetrics,
    prompts: promptDebugInfo,
    config: currentConfig,
    errors
  };
};
```

### API Calls Debug Panel

```typescript
interface APICallLog {
  id: string;
  timestamp: Date;
  method: string;
  url: string;
  requestBody?: any;
  responseBody?: any;
  responseTime: number;
  status: number;
  error?: string;
  headers: Record<string, string>;
}

const APICallsPanel: React.FC<{ calls: APICallLog[] }> = ({ calls }) => {
  const [selectedCall, setSelectedCall] = useState<APICallLog | null>(null);
  const [filter, setFilter] = useState<'all' | 'success' | 'error'>('all');

  const filteredCalls = calls.filter(call => {
    if (filter === 'error') return call.status >= 400;
    if (filter === 'success') return call.status < 400;
    return true;
  });

  return (
    <div className="api-calls-panel">
      <div className="panel-header">
        <h3>API Calls</h3>
        <select value={filter} onChange={(e) => setFilter(e.target.value as any)}>
          <option value="all">All</option>
          <option value="success">Success</option>
          <option value="error">Errors</option>
        </select>
      </div>
      
      <div className="calls-list">
        {filteredCalls.map(call => (
          <div 
            key={call.id}
            className={`call-item ${call.status >= 400 ? 'error' : 'success'}`}
            onClick={() => setSelectedCall(call)}
          >
            <div className="call-method">{call.method}</div>
            <div className="call-url">{call.url}</div>
            <div className="call-status">{call.status}</div>
            <div className="call-time">{call.responseTime}ms</div>
          </div>
        ))}
      </div>
      
      {selectedCall && (
        <APICallDetails 
          call={selectedCall} 
          onClose={() => setSelectedCall(null)} 
        />
      )}
    </div>
  );
};
```

### Message Debug View

```typescript
const MessageDebugView: React.FC<{ message: ChatMessage }> = ({ message }) => {
  const [activeTab, setActiveTab] = useState<'content' | 'metadata' | 'raw'>('content');
  
  return (
    <div className="message-debug">
      <div className="debug-tabs">
        <button 
          className={activeTab === 'content' ? 'active' : ''}
          onClick={() => setActiveTab('content')}
        >
          Content
        </button>
        <button 
          className={activeTab === 'metadata' ? 'active' : ''}
          onClick={() => setActiveTab('metadata')}
        >
          Metadata
        </button>
        <button 
          className={activeTab === 'raw' ? 'active' : ''}
          onClick={() => setActiveTab('raw')}
        >
          Raw JSON
        </button>
      </div>
      
      <div className="debug-content">
        {activeTab === 'content' && (
          <div className="content-view">
            <div className="rendered-content">
              <h4>Rendered:</h4>
              <div className="rendered">{message.content}</div>
            </div>
            <div className="raw-content">
              <h4>Raw Text:</h4>
              <pre>{message.content}</pre>
            </div>
          </div>
        )}
        
        {activeTab === 'metadata' && (
          <div className="metadata-view">
            <table className="metadata-table">
              <tbody>
                <tr><td>ID</td><td>{message.id}</td></tr>
                <tr><td>Role</td><td>{message.role}</td></tr>
                <tr><td>Timestamp</td><td>{message.timestamp.toISOString()}</td></tr>
                <tr><td>Tokens</td><td>{message.metadata?.tokens || 'N/A'}</td></tr>
                <tr><td>Model</td><td>{message.metadata?.model || 'N/A'}</td></tr>
                <tr><td>Error</td><td>{message.metadata?.error ? 'Yes' : 'No'}</td></tr>
              </tbody>
            </table>
          </div>
        )}
        
        {activeTab === 'raw' && (
          <pre className="raw-json">
            {JSON.stringify(message, null, 2)}
          </pre>
        )}
      </div>
    </div>
  );
};
```

### State Inspector

```typescript
const StateInspector: React.FC<{ state: any }> = ({ state }) => {
  const [expandedPaths, setExpandedPaths] = useState<Set<string>>(new Set());
  
  const togglePath = (path: string) => {
    const newPaths = new Set(expandedPaths);
    if (newPaths.has(path)) {
      newPaths.delete(path);
    } else {
      newPaths.add(path);
    }
    setExpandedPaths(newPaths);
  };
  
  return (
    <div className="state-inspector">
      <h3>Component State</h3>
      <JSONTree 
        data={state}
        theme="bright"
        invertTheme={false}
        shouldExpandNode={(keyPath) => expandedPaths.has(keyPath.join('.'))}
      />
      
      <div className="state-actions">
        <button onClick={() => navigator.clipboard.writeText(JSON.stringify(state, null, 2))}>
          Copy State
        </button>
        <button onClick={() => console.log('ChatBot State:', state)}>
          Log to Console
        </button>
      </div>
    </div>
  );
};
```

### Performance Panel

```typescript
interface PerformanceMetrics {
  messageRenderTime: number[];
  apiResponseTimes: number[];
  streamingLatency: number[];
  componentRerenders: number;
  memoryUsage?: number;
}

const PerformancePanel: React.FC<{ metrics: PerformanceMetrics }> = ({ metrics }) => {
  const avgRenderTime = metrics.messageRenderTime.reduce((a, b) => a + b, 0) / metrics.messageRenderTime.length;
  const avgResponseTime = metrics.apiResponseTimes.reduce((a, b) => a + b, 0) / metrics.apiResponseTimes.length;
  
  return (
    <div className="performance-panel">
      <h3>Performance Metrics</h3>
      
      <div className="metrics-grid">
        <div className="metric-item">
          <label>Avg Render Time</label>
          <span className={avgRenderTime > 16 ? 'warning' : 'good'}>
            {avgRenderTime.toFixed(2)}ms
          </span>
        </div>
        
        <div className="metric-item">
          <label>Avg API Response</label>
          <span className={avgResponseTime > 1000 ? 'warning' : 'good'}>
            {avgResponseTime.toFixed(0)}ms
          </span>
        </div>
        
        <div className="metric-item">
          <label>Component Rerenders</label>
          <span className={metrics.componentRerenders > 10 ? 'warning' : 'good'}>
            {metrics.componentRerenders}
          </span>
        </div>
        
        {metrics.memoryUsage && (
          <div className="metric-item">
            <label>Memory Usage</label>
            <span>{(metrics.memoryUsage / 1024 / 1024).toFixed(2)}MB</span>
          </div>
        )}
      </div>
      
      <div className="performance-charts">
        {/* Simple performance visualization */}
        <div className="chart-container">
          <h4>Message Render Times</h4>
          <div className="simple-chart">
            {metrics.messageRenderTime.slice(-20).map((time, index) => (
              <div 
                key={index}
                className="chart-bar"
                style={{ height: `${Math.min(time * 3, 100)}px` }}
                title={`${time.toFixed(2)}ms`}
              />
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};
```

### Prompt Viewer (JSX Prompt Debug)

```typescript
interface PromptDebugInfo {
  id: string;
  name: string;
  compiledPrompt: string;
  jsxSource: string;
  variables: Record<string, any>;
  timestamp: Date;
}

const PromptViewer: React.FC<{ prompts: PromptDebugInfo[] }> = ({ prompts }) => {
  const [selectedPrompt, setSelectedPrompt] = useState<PromptDebugInfo | null>(null);
  
  return (
    <div className="prompt-viewer">
      <h3>Prompt Debug</h3>
      
      <div className="prompts-list">
        {prompts.map(prompt => (
          <div 
            key={prompt.id}
            className="prompt-item"
            onClick={() => setSelectedPrompt(prompt)}
          >
            <div className="prompt-name">{prompt.name}</div>
            <div className="prompt-time">{prompt.timestamp.toLocaleTimeString()}</div>
          </div>
        ))}
      </div>
      
      {selectedPrompt && (
        <div className="prompt-details">
          <div className="prompt-tabs">
            <div className="tab-content">
              <h4>JSX Source</h4>
              <pre className="jsx-source">{selectedPrompt.jsxSource}</pre>
              
              <h4>Variables</h4>
              <pre className="variables">{JSON.stringify(selectedPrompt.variables, null, 2)}</pre>
              
              <h4>Compiled Prompt</h4>
              <pre className="compiled-prompt">{selectedPrompt.compiledPrompt}</pre>
            </div>
          </div>
          
          <div className="prompt-actions">
            <button onClick={() => navigator.clipboard.writeText(selectedPrompt.compiledPrompt)}>
              Copy Compiled Prompt
            </button>
            <button onClick={() => console.log('Prompt:', selectedPrompt)}>
              Log to Console
            </button>
          </div>
        </div>
      )}
    </div>
  );
};
```

### Live Configuration Editor

```typescript
const ConfigPanel: React.FC<{ 
  config: ChatBotConfig; 
  onConfigChange: (config: ChatBotConfig) => void;
}> = ({ config, onConfigChange }) => {
  const [localConfig, setLocalConfig] = useState(config);
  const [hasChanges, setHasChanges] = useState(false);
  
  const handleConfigUpdate = (key: keyof ChatBotConfig, value: any) => {
    const newConfig = { ...localConfig, [key]: value };
    setLocalConfig(newConfig);
    setHasChanges(true);
  };
  
  const applyChanges = () => {
    onConfigChange(localConfig);
    setHasChanges(false);
  };
  
  const resetChanges = () => {
    setLocalConfig(config);
    setHasChanges(false);
  };
  
  return (
    <div className="config-panel">
      <h3>Live Configuration</h3>
      
      <div className="config-form">
        <div className="config-group">
          <label>API Endpoint</label>
          <input 
            type="text"
            value={localConfig.apiEndpoint}
            onChange={(e) => handleConfigUpdate('apiEndpoint', e.target.value)}
          />
        </div>
        
        <div className="config-group">
          <label>Stream Responses</label>
          <input 
            type="checkbox"
            checked={localConfig.streamResponses}
            onChange={(e) => handleConfigUpdate('streamResponses', e.target.checked)}
          />
        </div>
        
        <div className="config-group">
          <label>Max Messages</label>
          <input 
            type="number"
            value={localConfig.maxMessages}
            onChange={(e) => handleConfigUpdate('maxMessages', parseInt(e.target.value))}
          />
        </div>
        
        <div className="config-group">
          <label>Theme</label>
          <select 
            value={localConfig.theme}
            onChange={(e) => handleConfigUpdate('theme', e.target.value)}
          >
            <option value="light">Light</option>
            <option value="dark">Dark</option>
            <option value="auto">Auto</option>
          </select>
        </div>
      </div>
      
      <div className="config-actions">
        <button 
          className="apply-btn"
          disabled={!hasChanges}
          onClick={applyChanges}
        >
          Apply Changes
        </button>
        <button 
          className="reset-btn"
          disabled={!hasChanges}
          onClick={resetChanges}
        >
          Reset
        </button>
      </div>
      
      <div className="config-export">
        <h4>Export Config</h4>
        <textarea 
          readOnly
          value={JSON.stringify(localConfig, null, 2)}
          className="config-json"
        />
        <button onClick={() => navigator.clipboard.writeText(JSON.stringify(localConfig, null, 2))}>
          Copy Config JSON
        </button>
      </div>
    </div>
  );
};
```

### Debug Panel Integration

```typescript
const DebugPanel: React.FC<{
  data: DebugData;
  position?: 'right' | 'bottom' | 'floating';
  defaultOpen?: boolean;
}> = ({ data, position = 'right', defaultOpen = false }) => {
  const [isOpen, setIsOpen] = useState(defaultOpen);
  const [activePanel, setActivePanel] = useState<string>('messages');
  
  const panels = [
    { key: 'messages', label: 'Messages', component: MessageDebugView },
    { key: 'api', label: 'API Calls', component: APICallsPanel },
    { key: 'state', label: 'State', component: StateInspector },
    { key: 'performance', label: 'Performance', component: PerformancePanel },
    { key: 'prompts', label: 'Prompts', component: PromptViewer },
    { key: 'config', label: 'Config', component: ConfigPanel }
  ];
  
  return (
    <div className={`debug-panel debug-panel--${position} ${isOpen ? 'open' : 'closed'}`}>
      <div className="debug-header">
        <h2>🐛 Debug Panel</h2>
        <button onClick={() => setIsOpen(!isOpen)}>
          {isOpen ? '✕' : '🔍'}
        </button>
      </div>
      
      {isOpen && (
        <>
          <div className="debug-tabs">
            {panels.map(panel => (
              <button
                key={panel.key}
                className={activePanel === panel.key ? 'active' : ''}
                onClick={() => setActivePanel(panel.key)}
              >
                {panel.label}
              </button>
            ))}
          </div>
          
          <div className="debug-content">
            {panels.map(panel => (
              <div 
                key={panel.key}
                className={`debug-panel-content ${activePanel === panel.key ? 'active' : 'hidden'}`}
              >
                <panel.component {...getPropsForPanel(panel.key, data)} />
              </div>
            ))}
          </div>
        </>
      )}
    </div>
  );
};
```

### Debug Keyboard Shortcuts

```typescript
const useDebugKeyboardShortcuts = (debugActions: DebugActions) => {
  useEffect(() => {
    const handleKeydown = (e: KeyboardEvent) => {
      if (e.ctrlKey && e.shiftKey) {
        switch (e.code) {
          case 'KeyD':
            e.preventDefault();
            debugActions.toggleDebugPanel();
            break;
          case 'KeyC':
            e.preventDefault();
            debugActions.clearLogs();
            break;
          case 'KeyE':
            e.preventDefault();
            debugActions.exportDebugData();
            break;
          case 'KeyR':
            e.preventDefault();
            debugActions.resetChatbot();
            break;
        }
      }
    };
    
    window.addEventListener('keydown', handleKeydown);
    return () => window.removeEventListener('keydown', handleKeydown);
  }, [debugActions]);
};
```

### Usage Example

```typescript
// Development usage with debug enabled
<ChatBot 
  apiEndpoint="/api/chat"
  enableDebug={true}
  debugPosition="right"
  debugDefaultOpen={false}
/>

// Access debug panel with URL parameter
// http://localhost:3000/chat?debug=true

// Or activate with keyboard shortcut: Ctrl+Shift+D
```

## Security Considerations

### Input Sanitization
```typescript
import { z } from 'zod';

const messageSchema = z.object({
  content: z.string()
    .min(1, 'Message cannot be empty')
    .max(4000, 'Message too long')
    .refine(val => !containsScripts(val), 'Invalid content detected')
});

const validateMessage = (content: string) => {
  return messageSchema.parse({ content });
};
```

### Rate Limiting
```typescript
const useRateLimit = (maxRequests: number, windowMs: number) => {
  const [requests, setRequests] = useState<number[]>([]);
  
  const canMakeRequest = useCallback(() => {
    const now = Date.now();
    const validRequests = requests.filter(time => now - time < windowMs);
    
    if (validRequests.length >= maxRequests) {
      return false;
    }
    
    setRequests([...validRequests, now]);
    return true;
  }, [requests, maxRequests, windowMs]);
  
  return { canMakeRequest };
};
```

### Debug Security
```typescript
// Ensure debug panel is only available in development
const isDebugAllowed = () => {
  return process.env.NODE_ENV === 'development' || 
         process.env.REACT_APP_ALLOW_DEBUG === 'true';
};

// Strip sensitive data from debug logs
const sanitizeDebugData = (data: any) => {
  const sanitized = { ...data };
  if (sanitized.config?.apiKey) {
    sanitized.config.apiKey = '***HIDDEN***';
  }
  return sanitized;
};
```

## Deployment & Integration

### As a Standalone Component
```typescript
// In customer applications
import { ChatBot } from '@fde/chatbot-component';

function App() {
  return (
    <div className="app">
      <ChatBot 
        apiEndpoint="https://customer1.api.com/chat"
        theme="light"
        placeholder="Ask me anything..."
      />
    </div>
  );
}
```

### As an Embedded Widget
```typescript
// Embeddable script for external websites
window.FDEChatBot = {
  init: (config) => {
    const container = document.getElementById('fde-chatbot');
    ReactDOM.render(<ChatBot {...config} />, container);
  }
};
```

This architecture provides a solid foundation that's simple to understand and implement, yet extensible enough to accommodate various customer requirements and future enhancements.