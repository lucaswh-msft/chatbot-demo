import { ChatMessage } from '../components/chatbot/types';

export const createUserMessage = (content: string): ChatMessage => ({
  id: generateMessageId(),
  content,
  role: 'user',
  timestamp: new Date(),
});

export const createAssistantMessage = (content: string, metadata?: Record<string, any>): ChatMessage => ({
  id: generateMessageId(),
  content,
  role: 'assistant',
  timestamp: new Date(),
  metadata,
});

export const createSystemMessage = (content: string): ChatMessage => ({
  id: generateMessageId(),
  content,
  role: 'system',
  timestamp: new Date(),
});

export const generateMessageId = (): string => {
  return `msg_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
};

export const formatTimestamp = (timestamp: Date): string => {
  return timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
};

export const truncateMessage = (content: string, maxLength: number = 100): string => {
  if (content.length <= maxLength) return content;
  return content.substring(0, maxLength) + '...';
};