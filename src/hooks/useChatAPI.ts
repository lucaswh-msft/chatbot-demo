import { useState, useCallback, useMemo } from 'react';
import { createAPIService } from '../services/mockAPI';
import { ChatBotConfig, ChatMessageRequest, ChatMessageResponse } from '../components/chatbot/types';

export const useChatAPI = (config: ChatBotConfig) => {
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const apiService = useMemo(() => createAPIService(config), [config]);

  const sendMessage = useCallback(async (request: ChatMessageRequest): Promise<ChatMessageResponse> => {
    setIsLoading(true);
    setError(null);

    try {
      const response = await apiService.sendMessage(request);
      return response;
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Unknown error occurred';
      setError(errorMessage);
      throw err;
    } finally {
      setIsLoading(false);
    }
  }, [apiService]);

  const getChatHistory = useCallback(async (sessionId: string, limit?: number) => {
    setIsLoading(true);
    setError(null);

    try {
      const history = await apiService.getChatHistory(sessionId, limit);
      return history;
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Unknown error occurred';
      setError(errorMessage);
      throw err;
    } finally {
      setIsLoading(false);
    }
  }, [apiService]);

  return {
    sendMessage,
    getChatHistory,
    isLoading,
    error,
    clearError: () => setError(null),
  };
};