import React, { useState } from 'react';
import { ChatBot } from './components/chatbot/ChatBot';
import { Demo } from './components/Demo';
import './App.css';

function App() {
  const [showDemo, setShowDemo] = useState(false);
  
  // Use mock API for development unless explicitly set to use real API
  const useRealAPI = process.env.REACT_APP_USE_REAL_API === 'true';
  const apiEndpoint = useRealAPI 
    ? (process.env.REACT_APP_CHAT_API_ENDPOINT || 'http://localhost:8001/api/chat')
    : 'mock://api/chat'; // Special mock endpoint

  const handleMessageSent = (message: string) => {
    console.log('Message sent:', message);
  };

  const handleResponseReceived = (response: string) => {
    console.log('Response received:', response);
  };

  if (showDemo) {
    return (
      <div className="App">
        <header className="App-header">
          <h1>Chatbot MVP Demo</h1>
          <p>Interactive demo with configurable options</p>
          <button 
            className="demo-toggle"
            onClick={() => setShowDemo(false)}
          >
            ← Back to Simple View
          </button>
        </header>
        
        <main className="App-main demo-main">
          <Demo />
        </main>
      </div>
    );
  }

  return (
    <div className="App">
      <header className="App-header">
        <h1>Chatbot MVP Demo</h1>
        <p>A lightweight, extensible chatbot component built with React/TypeScript</p>
        <button 
          className="demo-toggle"
          onClick={() => setShowDemo(true)}
        >
          Try Interactive Demo →
        </button>
      </header>
      
      <main className="App-main">
        <div className="chatbot-demo">
          <ChatBot
            apiEndpoint={apiEndpoint}
            theme="light"
            placeholder="Type your message here..."
            maxMessages={100}
            streamResponses={false}
            maxInputLength={4000}
            onMessageSent={handleMessageSent}
            onResponseReceived={handleResponseReceived}
            height="600px"
          />
        </div>
      </main>
      
      <footer className="App-footer">
        <p>Built with React, TypeScript, and modern web standards</p>
      </footer>
    </div>
  );
}

export default App;