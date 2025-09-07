import React, { useState } from 'react';
import { ChatBot } from './chatbot';
import './Demo.css';

export const Demo: React.FC = () => {
  const [theme, setTheme] = useState<'light' | 'dark'>('light');
  const [streaming, setStreaming] = useState(false);
  const [maxLength, setMaxLength] = useState(4000);

  const handleMessageSent = (message: string) => {
    console.log('Demo - Message sent:', message);
  };

  const handleResponseReceived = (response: string) => {
    console.log('Demo - Response received:', response);
  };

  return (
    <div className="demo-container">
      <div className="demo-controls">
        <h3>Chatbot Configuration</h3>
        
        <div className="control-group">
          <label>Theme:</label>
          <select value={theme} onChange={(e) => setTheme(e.target.value as 'light' | 'dark')}>
            <option value="light">Light</option>
            <option value="dark">Dark</option>
          </select>
        </div>

        <div className="control-group">
          <label>
            <input
              type="checkbox"
              checked={streaming}
              onChange={(e) => setStreaming(e.target.checked)}
            />
            Enable Streaming
          </label>
        </div>

        <div className="control-group">
          <label>Max Input Length:</label>
          <input
            type="number"
            value={maxLength}
            onChange={(e) => setMaxLength(parseInt(e.target.value))}
            min="100"
            max="10000"
            step="100"
          />
        </div>
      </div>

      <div className="demo-chatbot">
        <ChatBot
          apiEndpoint="http://localhost:8000/api/chat"
          theme={theme}
          streamResponses={streaming}
          maxInputLength={maxLength}
          placeholder={`Type a message... (max ${maxLength} chars)`}
          onMessageSent={handleMessageSent}
          onResponseReceived={handleResponseReceived}
          height="500px"
        />
      </div>
    </div>
  );
};