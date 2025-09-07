export const chatConfig = {
  apiEndpoint: process.env.REACT_APP_CHAT_API_ENDPOINT || '/api/chat',
  enableStreaming: process.env.REACT_APP_ENABLE_STREAMING === 'true',
  maxMessages: parseInt(process.env.REACT_APP_MAX_MESSAGES || '100'),
  enableAnalytics: process.env.REACT_APP_ENABLE_ANALYTICS === 'true',
  useRealAPI: process.env.REACT_APP_USE_REAL_API === 'true',
};

// Customer-specific configurations can be added here
export const defaultConfig = {
  theme: 'light' as const,
  maxInputLength: 4000,
  enableFileUpload: false,
  streamResponses: false,
  placeholder: 'Type a message...',
};