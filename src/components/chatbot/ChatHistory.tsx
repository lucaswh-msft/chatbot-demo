import React, { useEffect, useRef } from 'react';
import { ChatMessage } from './ChatMessage';
import { ChatMessage as ChatMessageType } from './types';

interface ChatHistoryProps {
  messages: ChatMessageType[];
  customMessageRenderer?: (message: ChatMessageType) => React.ReactNode;
  autoScroll?: boolean;
}

export const ChatHistory: React.FC<ChatHistoryProps> = ({
  messages,
  customMessageRenderer,
  autoScroll = true,
}) => {
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const containerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (autoScroll && messagesEndRef.current && messagesEndRef.current.scrollIntoView) {
      messagesEndRef.current.scrollIntoView({ behavior: 'smooth' });
    }
  }, [messages, autoScroll]);

  if (messages.length === 0) {
    return (
      <div className="chat-history empty">
        <div className="empty-state">
          <p>Start a conversation by typing a message below.</p>
        </div>
      </div>
    );
  }

  return (
    <div ref={containerRef} className="chat-history">
      <div className="messages-container">
        {messages.map((message) => (
          <ChatMessage
            key={message.id}
            message={message}
            customRenderer={customMessageRenderer}
          />
        ))}
        <div ref={messagesEndRef} />
      </div>
    </div>
  );
};