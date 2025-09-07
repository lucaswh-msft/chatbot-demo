import React, { useState, useCallback, KeyboardEvent } from 'react';

interface ChatInputProps {
  onSendMessage: (message: string) => void;
  disabled?: boolean;
  placeholder?: string;
  maxLength?: number;
  isLoading?: boolean;
  onStopGeneration?: () => void;
}

export const ChatInput: React.FC<ChatInputProps> = ({
  onSendMessage,
  disabled = false,
  placeholder = 'Type a message...',
  maxLength = 4000,
  isLoading = false,
  onStopGeneration,
}) => {
  const [input, setInput] = useState('');

  const handleSubmit = useCallback((e: React.FormEvent) => {
    e.preventDefault();
    
    if (!input.trim() || disabled || isLoading) {
      return;
    }

    onSendMessage(input.trim());
    setInput('');
  }, [input, disabled, isLoading, onSendMessage]);

  const handleKeyPress = useCallback((e: KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit(e);
    }
  }, [handleSubmit]);

  const handleStop = useCallback(() => {
    onStopGeneration?.();
  }, [onStopGeneration]);

  return (
    <form onSubmit={handleSubmit} className="chat-input-form">
      <div className="input-container">
        <textarea
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyPress={handleKeyPress}
          placeholder={placeholder}
          disabled={disabled}
          maxLength={maxLength}
          rows={1}
          className="message-input"
        />
        <div className="input-actions">
          {isLoading ? (
            <button
              type="button"
              onClick={handleStop}
              className="stop-button"
              title="Stop generation"
            >
              ⏹
            </button>
          ) : (
            <button
              type="submit"
              disabled={!input.trim() || disabled}
              className="send-button"
              title="Send message"
            >
              ➤
            </button>
          )}
        </div>
      </div>
      <div className="input-footer">
        <span className="character-count">
          {input.length}/{maxLength}
        </span>
      </div>
    </form>
  );
};