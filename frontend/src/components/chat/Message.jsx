
import React from "react";

function Message({ message, currentUser }) {
  if (!message?.user || !currentUser) return null;

  const isMe = message.user.id === currentUser.id;

  return (
    <div className={`bubble ${isMe ? "me" : "other"}`}>
      <div className="bubble-header">
        <span className="author">{message.user.username}</span>
        <span className="time">
          {new Date(message.timestamp).toLocaleTimeString([], {
            hour: "2-digit",
            minute: "2-digit",
          })}
        </span>
      </div>
      <div className="bubble-content">{message.content}</div>
    </div>
  );
}

export default Message;
