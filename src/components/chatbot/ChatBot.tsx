import React, { useCallback } from 'react';
import { ChatBotProps } from './types';
import { useChatBot } from '../../hooks/useChatBot';
import { ChatHeader } from './ChatHeader';
import { ChatHistory } from './ChatHistory';
import { ChatInput } from './ChatInput';
import './ChatBot.css';

export const ChatBot: React.FC<ChatBotProps> = ({
  apiEndpoint,
  apiKey,
  theme = 'light',
  placeholder = 'Type a message...',
  maxMessages = 100,
  streamResponses = false,
  allowFileUpload = false,
  maxInputLength = 4000,
  customMessageRenderer,
  onMessageSent,
  onResponseReceived,
  className = '',
  height = '600px',
}) => {
  const config = {
    apiEndpoint,
    apiKey,
    streamResponses,
    maxMessages,
    maxInputLength,
  };

  const {
    messages,
    sendMessage,
    stopGeneration,
    clearChat,
    isLoading,
    isStreaming,
    error,
  } = useChatBot(config);

  const handleSendMessage = useCallback(async (content: string) => {
    try {
      onMessageSent?.(content);
      await sendMessage(content);
      
      // Get the last assistant message for the callback
      const lastMessage = messages[messages.length - 1];
      if (lastMessage && lastMessage.role === 'assistant') {
        onResponseReceived?.(lastMessage.content);
      }
    } catch (err) {
      console.error('Failed to send message:', err);
    }
  }, [sendMessage, onMessageSent, onResponseReceived, messages]);

  const handleClearChat = useCallback(() => {
    if (window.confirm('Are you sure you want to clear the conversation?')) {
      clearChat();
    }
  }, [clearChat]);

  return (
    <div 
      className={`chatbot-container ${theme} ${className}`}
      style={{ height }}
      data-testid="chatbot-container"
    >
      <ChatHeader
        title="Chat Assistant"
        subtitle={error ? `Error: ${error}` : undefined}
        isOnline={!error}
        onClearChat={handleClearChat}
        showClearButton={messages.length > 0}
      />
      
      <ChatHistory
        messages={messages}
        customMessageRenderer={customMessageRenderer}
      />
      
      <ChatInput
        onSendMessage={handleSendMessage}
        onStopGeneration={stopGeneration}
        disabled={!!error}
        placeholder={placeholder}
        maxLength={maxInputLength}
        isLoading={isLoading}
      />
      
      {error && (
        <div className="error-banner">
          <span className="error-message">{error}</span>
        </div>
      )}
    </div>
  );
};