import { useCallback, useState, useMemo } from 'react';
import { useChatMessages } from './useChatMessages';
import { useChatAPI } from './useChatAPI';
import { useChatStream } from './useChatStream';
import { ChatBotConfig, ChatMessage } from '../components/chatbot/types';
import { createUserMessage, createAssistantMessage } from '../utils/messageFormatter';
import { validateMessage } from '../utils/validation';

export const useChatBot = (config: ChatBotConfig) => {
  const [sessionId] = useState(() => `session_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`);
  
  const {
    messages,
    addMessage,
    updateMessage,
    clearMessages,
    getLastMessage,
  } = useChatMessages(config.maxMessages);

  const { sendMessage: apiSendMessage, isLoading: apiLoading, error: apiError } = useChatAPI(config);
  const { startStream, stopStream, isStreaming, error: streamError } = useChatStream(config);

  const isLoading = apiLoading || isStreaming;
  const error = apiError || streamError;

  const handleSendMessage = useCallback(async (content: string): Promise<void> => {
    // Validate message
    const validationError = validateMessage(content, config.maxInputLength);
    if (validationError) {
      throw new Error(validationError);
    }

    // Create and add user message
    const userMessage = createUserMessage(content);
    addMessage(userMessage);

    const request = {
      content,
      session_id: sessionId,
    };

    try {
      if (config.streamResponses) {
        // Handle streaming response
        const assistantMessage = createAssistantMessage('', { streaming: true });
        addMessage(assistantMessage);

        let fullContent = '';
        
        await startStream(
          request,
          (chunk: string) => {
            fullContent += chunk;
            updateMessage(assistantMessage.id, { 
              content: fullContent,
              metadata: { ...assistantMessage.metadata, streaming: true }
            });
          },
          () => {
            updateMessage(assistantMessage.id, { 
              metadata: { ...assistantMessage.metadata, streaming: false }
            });
          },
          (error: string) => {
            updateMessage(assistantMessage.id, { 
              content: `Error: ${error}`,
              metadata: { ...assistantMessage.metadata, error: true, streaming: false }
            });
          }
        );
      } else {
        // Handle regular response
        const response = await apiSendMessage(request);
        const assistantMessage = createAssistantMessage(response.content, response.metadata);
        addMessage(assistantMessage);
      }
    } catch (err) {
      // Add error message
      const errorMessage = createAssistantMessage(
        `Sorry, I encountered an error: ${err instanceof Error ? err.message : 'Unknown error'}`,
        { error: true }
      );
      addMessage(errorMessage);
      throw err;
    }
  }, [
    config,
    sessionId,
    addMessage,
    updateMessage,
    apiSendMessage,
    startStream,
  ]);

  const handleStopGeneration = useCallback(() => {
    if (isStreaming) {
      stopStream();
    }
  }, [isStreaming, stopStream]);

  const handleClearChat = useCallback(() => {
    clearMessages();
  }, [clearMessages]);

  return {
    messages,
    sendMessage: handleSendMessage,
    stopGeneration: handleStopGeneration,
    clearChat: handleClearChat,
    isLoading,
    isStreaming,
    error,
    sessionId,
    getLastMessage,
  };
};