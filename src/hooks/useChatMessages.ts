import { useState, useCallback } from 'react';
import { ChatMessage } from '../components/chatbot/types';

export const useChatMessages = (maxMessages?: number) => {
  const [messages, setMessages] = useState<ChatMessage[]>([]);

  const addMessage = useCallback((message: ChatMessage) => {
    setMessages(prev => {
      const newMessages = [...prev, message];
      
      // Limit messages if maxMessages is specified
      if (maxMessages && newMessages.length > maxMessages) {
        return newMessages.slice(-maxMessages);
      }
      
      return newMessages;
    });
  }, [maxMessages]);

  const updateMessage = useCallback((messageId: string, updates: Partial<ChatMessage>) => {
    setMessages(prev => 
      prev.map(msg => 
        msg.id === messageId 
          ? { ...msg, ...updates }
          : msg
      )
    );
  }, []);

  const removeMessage = useCallback((messageId: string) => {
    setMessages(prev => prev.filter(msg => msg.id !== messageId));
  }, []);

  const clearMessages = useCallback(() => {
    setMessages([]);
  }, []);

  const getLastMessage = useCallback(() => {
    return messages[messages.length - 1] || null;
  }, [messages]);

  return {
    messages,
    addMessage,
    updateMessage,
    removeMessage,
    clearMessages,
    getLastMessage,
  };
};