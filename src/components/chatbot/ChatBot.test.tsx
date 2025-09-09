import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { ChatBot } from './ChatBot';

// Mock the API service
const mockSendMessage = jest.fn().mockResolvedValue({
  id: 'test-response',
  content: 'Hello! This is a test response.',
  role: 'assistant',
  timestamp: new Date().toISOString(),
  metadata: { tokens: 10 }
});

const mockStreamMessage = jest.fn();
const mockGetChatHistory = jest.fn().mockResolvedValue([]);

jest.mock('../../services/mockAPI', () => ({
  createAPIService: () => ({
    sendMessage: mockSendMessage,
    streamMessage: mockStreamMessage,
    getChatHistory: mockGetChatHistory
  })
}));

const defaultProps = {
  apiEndpoint: 'http://localhost:8001/api/chat',
  theme: 'light' as const,
  placeholder: 'Type a message...',
  height: '600px'
};

describe('ChatBot Component', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('renders without crashing', () => {
    render(<ChatBot {...defaultProps} />);
    // Check that the main container renders
    expect(screen.getByTestId('chatbot-container')).toBeInTheDocument();
  });

  it('displays the correct placeholder text', () => {
    render(<ChatBot {...defaultProps} />);
    expect(screen.getByPlaceholderText('Type a message...')).toBeInTheDocument();
  });

  it('allows typing in the input field', () => {
    render(<ChatBot {...defaultProps} />);
    const input = screen.getByPlaceholderText('Type a message...') as HTMLTextAreaElement;
    
    fireEvent.change(input, { target: { value: 'Hello world' } });
    expect(input.value).toBe('Hello world');
  });

  it('applies custom className when provided', () => {
    render(<ChatBot {...defaultProps} className="custom-chatbot" />);
    const container = screen.getByTestId('chatbot-container');
    expect(container).toHaveClass('custom-chatbot');
  });

  it('displays send button correctly', () => {
    render(<ChatBot {...defaultProps} />);
    const sendButton = screen.getByTitle('Send message');
    expect(sendButton).toBeInTheDocument();
    expect(sendButton).toBeDisabled(); // Should be disabled when input is empty
  });
});