import { ChatMessageRequest, ChatMessageResponse, ChatBotConfig } from '../components/chatbot/types';

export class ChatAPIService {
  private config: ChatBotConfig;

  constructor(config: ChatBotConfig) {
    this.config = config;
  }

  async sendMessage(request: ChatMessageRequest): Promise<ChatMessageResponse> {
    const response = await fetch(`${this.config.apiEndpoint}/messages`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        ...(this.config.apiKey && { 'Authorization': `Bearer ${this.config.apiKey}` }),
      },
      body: JSON.stringify(request),
    });

    if (!response.ok) {
      throw new Error(`API Error: ${response.status} ${response.statusText}`);
    }

    return await response.json();
  }

  async getChatHistory(sessionId: string, limit: number = 50): Promise<ChatMessageResponse[]> {
    const response = await fetch(
      `${this.config.apiEndpoint}/messages/${sessionId}?limit=${limit}`,
      {
        headers: {
          ...(this.config.apiKey && { 'Authorization': `Bearer ${this.config.apiKey}` }),
        },
      }
    );

    if (!response.ok) {
      throw new Error(`API Error: ${response.status} ${response.statusText}`);
    }

    return await response.json();
  }

  async *streamMessage(request: ChatMessageRequest): AsyncGenerator<string, void, unknown> {
    const response = await fetch(`${this.config.apiEndpoint}/stream`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        ...(this.config.apiKey && { 'Authorization': `Bearer ${this.config.apiKey}` }),
      },
      body: JSON.stringify(request),
    });

    if (!response.ok) {
      throw new Error(`API Error: ${response.status} ${response.statusText}`);
    }

    const reader = response.body?.getReader();
    if (!reader) {
      throw new Error('No response body reader available');
    }

    const decoder = new TextDecoder();

    try {
      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        const chunk = decoder.decode(value, { stream: true });
        const lines = chunk.split('\n');

        for (const line of lines) {
          if (line.startsWith('data: ')) {
            const data = line.slice(6);
            if (data === '[DONE]') return;
            
            try {
              const parsed = JSON.parse(data);
              if (parsed.content) {
                yield parsed.content;
              }
            } catch (e) {
              // Skip invalid JSON lines
              continue;
            }
          }
        }
      }
    } finally {
      reader.releaseLock();
    }
  }
}