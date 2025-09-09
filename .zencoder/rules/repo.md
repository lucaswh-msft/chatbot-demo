---
description: Repository Information Overview
alwaysApply: true
---

# Repository Information Overview

## Repository Summary
A lightweight, extensible chatbot component built with React/TypeScript that integrates with FastAPI backends. The project provides a customizable chat interface with features like streaming support, responsive design, and TypeScript integration.

## Repository Structure
- **src/**: Frontend source code containing React components, hooks, services, and utilities
  - **components/**: UI components including the main chatbot components
  - **hooks/**: Custom React hooks for chat functionality
  - **services/**: API integration services
  - **utils/**: Utility functions for message formatting and validation
- **public/**: Static assets and HTML template
- **build/**: Production build output
- **backend/**: FastAPI backend service for chat functionality
- **spec/**: API specifications and documentation

## Main Repository Components
- **Frontend**: React/TypeScript chatbot component with customizable UI
- **Backend**: FastAPI service providing chat API endpoints
- **Configuration**: Environment variables for customizing behavior

## Projects

### Frontend (React Component)
**Configuration File**: package.json

#### Language & Runtime
**Language**: TypeScript/JavaScript
**Version**: TypeScript 4.9.x
**Build System**: React Scripts (Create React App)
**Package Manager**: npm

#### Dependencies
**Main Dependencies**:
- React 18.2.0
- React DOM 18.2.0
- TypeScript 4.9.0
- Zod 3.22.0
- React Scripts 5.0.1

**Development Dependencies**:
- Testing Library (Jest DOM 5.17.0, React 13.4.0, User Event 14.6.1)
- TypeScript types (@types/jest, @types/node, @types/react, @types/react-dom)

#### Build & Installation
```bash
# Install dependencies
npm install

# Start development server
npm start

# Build for production
npm run build
```

#### Configuration
**Environment Variables**:
- REACT_APP_CHAT_API_ENDPOINT: Backend API endpoint
- REACT_APP_ENABLE_STREAMING: Enable/disable streaming responses
- REACT_APP_MAX_MESSAGES: Maximum messages to keep in history
- REACT_APP_USE_REAL_API: Toggle between real and mock API
- PORT: Development server port (default: 3001)

#### Testing
**Framework**: Jest with React Testing Library
**Test Location**: Component tests are co-located with components (e.g., ChatBot.test.tsx)
**Configuration**: Standard Create React App test setup with Jest
**Run Command**:
```bash
npm test
```

#### Component Architecture
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

**API Services**:
- chatAPI.ts: Real API service
- mockAPI.ts: Mock service for development
- basaltAdapterAPI.ts: Adapter for Basalt API integration

### Backend (FastAPI)
**Configuration File**: backend/requirements.txt

#### Language & Runtime
**Language**: Python
**Version**: Python 3.13.x
**Framework**: FastAPI 0.112.2
**Package Manager**: pip

#### Dependencies
**Main Dependencies**:
- fastapi 0.112.2
- uvicorn 0.30.3
- pydantic 2.8.2

#### Build & Installation
```bash
# Create and activate virtual environment
python -m venv .venv
.venv\Scripts\activate

# Install dependencies
pip install -r backend/requirements.txt

# Run development server
uvicorn backend.main:app --reload --port 8001
```

#### API Endpoints
**Main Endpoints**:
- POST /services/conversation/web/api/v1/unified-chat/caip/init: Initialize chat session
- POST /services/conversation/web/api/v1/unified-chat/caip/message: Send message and get response
- GET /health: Health check endpoint

**Models**:
- ChatMessageRequest: User message request
- ChatMessageResponse: AI assistant response
- ChatMessage: Message data structure