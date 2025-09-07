---
description: Repository Information Overview
alwaysApply: true
---

# Chatbot MVP Information

## Summary
A lightweight, extensible chatbot component built with React/TypeScript that integrates with FastAPI backends. The project provides a customizable chat interface with features like streaming support, responsive design, and TypeScript integration.

## Structure
- **src/**: Source code containing React components, hooks, services, and utilities
  - **components/**: UI components including the main chatbot components
  - **hooks/**: Custom React hooks for chat functionality
  - **services/**: API integration services
  - **utils/**: Utility functions for message formatting and validation
- **public/**: Static assets and HTML template
- **build/**: Production build output

## Language & Runtime
**Language**: TypeScript/JavaScript
**Version**: TypeScript 4.9.x
**Build System**: React Scripts (Create React App)
**Package Manager**: npm

## Dependencies
**Main Dependencies**:
- React 18.2.0
- React DOM 18.2.0
- TypeScript 4.9.0
- Zod 3.22.0
- React Scripts 5.0.1

**Development Dependencies**:
- Testing Library (Jest DOM 5.17.0, React 13.4.0, User Event 14.6.1)
- TypeScript types (@types/jest, @types/node, @types/react, @types/react-dom)

## Build & Installation
```bash
# Install dependencies
npm install

# Start development server
npm start

# Build for production
npm run build
```

## Configuration
**Environment Variables**:
- REACT_APP_CHAT_API_ENDPOINT: Backend API endpoint
- REACT_APP_ENABLE_STREAMING: Enable/disable streaming responses
- REACT_APP_MAX_MESSAGES: Maximum messages to keep in history
- REACT_APP_USE_REAL_API: Toggle between real and mock API

## Testing
**Framework**: Jest with React Testing Library
**Test Location**: Component tests are co-located with components (e.g., ChatBot.test.tsx)
**Configuration**: Standard Create React App test setup with Jest
**Run Command**:
```bash
npm test
```

## Component Architecture
**Main Components**:
- ChatBot: Main container component
- ChatMessage: Individual message display
- ChatInput: User input component
- ChatHistory: Message history display
- ChatHeader: Header component

**Custom Hooks**:
- useChatBot: Main logic hook
- useChatMessages: Message state management
- useChatAPI: API integration
- useChatStream: Streaming support

**API Integration**:
- chatAPI.ts: Real API service
- mockAPI.ts: Mock service for development