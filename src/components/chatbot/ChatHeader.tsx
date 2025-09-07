import React from 'react';

interface ChatHeaderProps {
  title?: string;
  subtitle?: string;
  isOnline?: boolean;
  onClearChat?: () => void;
  showClearButton?: boolean;
}

export const ChatHeader: React.FC<ChatHeaderProps> = ({
  title = 'Chat Assistant',
  subtitle,
  isOnline = true,
  onClearChat,
  showClearButton = true,
}) => {
  return (
    <div className="chat-header">
      <div className="header-content">
        <div className="header-info">
          <h3 className="chat-title">{title}</h3>
          {subtitle && <p className="chat-subtitle">{subtitle}</p>}
        </div>
        <div className="header-status">
          <div className={`status-indicator ${isOnline ? 'online' : 'offline'}`}>
            <span className="status-dot"></span>
            <span className="status-text">
              {isOnline ? 'Online' : 'Offline'}
            </span>
          </div>
        </div>
      </div>
      {showClearButton && onClearChat && (
        <div className="header-actions">
          <button
            onClick={onClearChat}
            className="clear-button"
            title="Clear conversation"
          >
            🗑
          </button>
        </div>
      )}
    </div>
  );
};