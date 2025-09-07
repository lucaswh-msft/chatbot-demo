import { useState, useCallback, useRef, useMemo } from 'react';
import { createAPIService } from '../services/mockAPI';
import { ChatBotConfig, ChatMessageRequest } from '../components/chatbot/types';

export const useChatStream = (config: ChatBotConfig) => {
  const [isStreaming, setIsStreaming] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const abortControllerRef = useRef<AbortController | null>(null);

  const apiService = useMemo(() => createAPIService(config), [config]);

  const startStream = useCallback(async (
    request: ChatMessageRequest,
    onChunk: (chunk: string) => void,
    onComplete?: () => void,
    onError?: (error: string) => void
  ) => {
    if (isStreaming) {
      throw new Error('Stream already in progress');
    }

    setIsStreaming(true);
    setError(null);
    abortControllerRef.current = new AbortController();

    try {
      const streamGenerator = apiService.streamMessage(request);
      
      for await (const chunk of streamGenerator) {
        if (abortControllerRef.current?.signal.aborted) {
          break;
        }
        onChunk(chunk);
      }
      
      onComplete?.();
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Streaming error occurred';
      setError(errorMessage);
      onError?.(errorMessage);
    } finally {
      setIsStreaming(false);
      abortControllerRef.current = null;
    }
  }, [apiService, isStreaming]);

  const stopStream = useCallback(() => {
    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
      abortControllerRef.current = null;
    }
    setIsStreaming(false);
  }, []);

  return {
    startStream,
    stopStream,
    isStreaming,
    error,
    clearError: () => setError(null),
  };
};