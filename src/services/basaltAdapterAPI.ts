import { ChatMessageRequest, ChatMessageResponse, ChatBotConfig } from '../components/chatbot/types';

// Adapter service to translate our ChatMessageRequest/Response to Basalt-like API
export class BasaltAdapterAPIService {
  private config: ChatBotConfig;

  constructor(config: ChatBotConfig) {
    this.config = config;
  }

  private get baseUrl() {
    return this.config.apiEndpoint.replace(/\/$/, '');
  }

  async sendMessage(request: ChatMessageRequest): Promise<ChatMessageResponse> {
    // First call init if needed (client/session bootstrap). Here we mock minimal required shape.
    const conversationId = request.context?.conversationId || request.session_id || 'conv_mock';

    // Build Basalt message payload
    const nowISO = new Date().toISOString();

    const payload = {
      client: {
        firstName: null,
        lastName: null,
        email: null,
        phoneNumber: null,
        memberships: { isBetaMember: false, isTotalTechSupport: false },
        membershipList: [],
        orderId: ''
      },
      id: cryptoRandomId(),
      message: {
        turnId: 1,
        msgTimestamp: nowISO,
        latLong: null,
        metadata: {
          more: {
            membershipState: 'No',
            logInState: 'loggedOut',
            referer: 'web',
            botSource: 'dfcx',
            requestedProductDataType: request.context?.requestedProductDataType || 'drawer',
          },
          correlationId: cryptoRandomId(),
          conversationId,
          genAI: true
        },
        message: request.content,
        msgSource: 'user_typed'
      },
      connection: 'connected',
      provider: {
        currentProvider: 'caip',
        queue: null,
        previousProvider: null,
        channel: 'chat',
        pillar: null,
        category: null,
        chatAttributes: null
      },
      requestedAgentPool: 'caip',
      requestedAgentQueue: null,
      clientId: conversationId,
      caipConversationId: conversationId,
      paidMember: false,
      loggedInAtInitChat: false,
      isNative: true,
      chatSessionStart: null,
      mediaTrack: 'text'
    };

    const resp = await fetch(`${this.baseUrl}/services/conversation/web/api/v1/unified-chat/caip/message`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        ...(this.config.apiKey && { 'Authorization': `Bearer ${this.config.apiKey}` }),
      },
      body: JSON.stringify(payload)
    });

    if (!resp.ok) {
      throw new Error(`API Error: ${resp.status} ${resp.statusText}`);
    }

    const data = await resp.json();
    // Map Basalt response to ChatMessageResponse (take first textual message)
    const displayText: string = data?.messages?.[0]?.displayText || '';

    return {
      id: `msg_${Date.now()}`,
      content: displayText,
      role: 'assistant',
      timestamp: new Date().toISOString(),
      metadata: { provider: 'basalt' }
    };
  }

  // Streaming is not supported by the Basalt API; provide a compatible stub
  async *streamMessage(request: ChatMessageRequest): AsyncGenerator<string, void, unknown> {
    const response = await this.sendMessage(request);
    // Yield the full response as a single chunk to satisfy the interface
    yield response.content;
  }

  async getChatHistory(sessionId: string, limit: number = 50): Promise<ChatMessageResponse[]> {
    // Not defined in schema; return empty for now
    return [];
  }
}

export const createBasaltAdapterService = (config: ChatBotConfig) => new BasaltAdapterAPIService(config);

function cryptoRandomId(): string {
  // Simple random id without relying on Node crypto in browser environments
  return Math.random().toString(36).slice(2) + Math.random().toString(36).slice(2);
}