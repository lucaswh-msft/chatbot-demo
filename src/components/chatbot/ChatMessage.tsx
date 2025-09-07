import React from 'react';
import { ChatMessage as ChatMessageType } from './types';
import { formatTimestamp } from '../../utils/messageFormatter';

interface ChatMessageProps {
  message: ChatMessageType;
  customRenderer?: (message: ChatMessageType) => React.ReactNode;
}

export const ChatMessage: React.FC<ChatMessageProps> = ({ message, customRenderer }) => {
  if (customRenderer) {
    return <>{customRenderer(message)}</>;
  }

  const isUser = message.role === 'user';
  const isError = message.metadata?.error;
  const isStreaming = message.metadata?.streaming;

  return (
    <div className={`chat-message ${isUser ? 'user' : 'assistant'} ${isError ? 'error' : ''}`}>
      <div className="message-header">
        <span className="message-role">
          {isUser ? 'You' : 'Assistant'}
        </span>
        <span className="message-timestamp">
          {formatTimestamp(message.timestamp)}
        </span>
        {isStreaming && (
          <span className="streaming-indicator">●</span>
        )}
      </div>
      <div className="message-content">
        {message.content}
        {isStreaming && !message.content && (
          <span className="typing-indicator">Thinking...</span>
        )}
      </div>
      {message.metadata?.tokens && (
        <div className="message-metadata">
          {message.metadata.tokens} tokens
        </div>
      )}
    </div>
  );
};