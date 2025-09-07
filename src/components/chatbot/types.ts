import { ReactNode } from 'react';

export interface ChatMessage {
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

export interface ChatBotProps {
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

export interface ChatBotConfig {
  apiEndpoint: string;
  apiKey?: string;
  streamResponses?: boolean;
  maxMessages?: number;
  maxInputLength?: number;
}

export interface ChatMessageRequest {
  content: string;
  session_id?: string;
  context?: Record<string, any>;
}

export interface ChatMessageResponse {
  id: string;
  content: string;
  role: 'assistant';
  timestamp: string;
  metadata?: Record<string, any>;
}