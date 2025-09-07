// Main component exports
export { ChatBot } from './ChatBot';
export { ChatMessage } from './ChatMessage';
export { ChatInput } from './ChatInput';
export { ChatHistory } from './ChatHistory';
export { ChatHeader } from './ChatHeader';

// Type exports
export type {
  ChatBotProps,
  ChatMessage as ChatMessageType,
  ChatBotConfig,
  ChatMessageRequest,
  ChatMessageResponse,
} from './types';

// Hook exports
export { useChatBot } from '../../hooks/useChatBot';
export { useChatMessages } from '../../hooks/useChatMessages';
export { useChatAPI } from '../../hooks/useChatAPI';
export { useChatStream } from '../../hooks/useChatStream';

// Utility exports
export { createUserMessage, createAssistantMessage, formatTimestamp } from '../../utils/messageFormatter';
export { validateMessage } from '../../utils/validation';