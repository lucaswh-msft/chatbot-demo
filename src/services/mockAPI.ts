import { ChatMessageRequest, ChatMessageResponse } from '../components/chatbot/types';
import { createBasaltAdapterService } from './basaltAdapterAPI';

// Mock responses for development
const mockResponses = [
  "Hello! I'm a chatbot assistant. How can I help you today?",
  "That's an interesting question. Let me think about that...",
  "I understand what you're asking. Here's what I think:",
  "Thanks for sharing that with me. I'd be happy to help.",
  "That's a great point. Let me provide some more information:",
  "I see what you mean. Here's my perspective on that:",
  "Absolutely! I can definitely help you with that.",
  "That's a common question. Here's what you should know:",
];

const getRandomResponse = (): string => {
  return mockResponses[Math.floor(Math.random() * mockResponses.length)];
};

const delay = (ms: number) => new Promise(resolve => setTimeout(resolve, ms));

export class MockChatAPIService {
  async sendMessage(request: ChatMessageRequest): Promise<ChatMessageResponse> {
    // Simulate network delay
    await delay(1000 + Math.random() * 2000);
    
    // Simulate occasional errors (5% chance)
    if (Math.random() < 0.05) {
      throw new Error('Network error: Unable to connect to chat service');
    }

    const response: ChatMessageResponse = {
      id: `msg_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
      content: getRandomResponse(),
      role: 'assistant',
      timestamp: new Date().toISOString(),
      metadata: {
        tokens: Math.floor(Math.random() * 100) + 20,
        model: 'mock-gpt-3.5',
      },
    };

    return response;
  }

  async *streamMessage(request: ChatMessageRequest): AsyncGenerator<string, void, unknown> {
    // Simulate streaming delay
    await delay(500);
    
    const fullResponse = getRandomResponse();
    const words = fullResponse.split(' ');
    
    for (const word of words) {
      await delay(100 + Math.random() * 200);
      yield word + ' ';
    }
  }

  async getChatHistory(sessionId: string, limit: number = 50): Promise<ChatMessageResponse[]> {
    // Return empty history for mock
    return [];
  }
}

// Override the real API service with mock in development
export const createAPIService = (config: any) => {
  // Use mock API unless explicitly set to use real API
  const useRealAPI = process.env.REACT_APP_USE_REAL_API === 'true';
  
  if (!useRealAPI || config.apiEndpoint?.startsWith('mock://')) {
    return new MockChatAPIService();
  }
  
  // Use the Basalt adapter as the real API service
  return createBasaltAdapterService(config);
};