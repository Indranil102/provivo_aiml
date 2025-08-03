// src/components/Chat/Message.jsx
import React from "react";

function Message({ message, currentUser }) {
  // defensive: skip rendering if user is missing
  if (!message?.user || !currentUser) return null;

  const isCurrentUser = message.user.id === currentUser.id;

  return (
    <div className={`message ${isCurrentUser ? "message-sent" : "message-received"}`}>
      <div className="message-header">
        <span className="message-author">{message.user.username}</span>
        <span className="message-time">
          {new Date(message.timestamp).toLocaleTimeString()}
        </span>
      </div>
      <div className="message-content">{message.content}</div>
    </div>
  );
}

export default Message;