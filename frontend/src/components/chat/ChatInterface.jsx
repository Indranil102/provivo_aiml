// src/components/Chat/ChatInterface.jsx
import React, { useState, useEffect } from "react";
import { useAuth } from "../../services/auth";
import api, { fetchGroup } from "../../services/api";
import Message from "./Message";
import MeetingScheduler from "../Metting/MeetingSchedular";
import "./Chat.css";

function ChatInterface() {
  const { user } = useAuth();
  const [messages, setMessages] = useState([]);
  const [newMessage, setNewMessage] = useState("");
  const [loading, setLoading] = useState(false);
  const [pendingMeeting, setPendingMeeting] = useState(null);
  const [group, setGroup] = useState(null);

  /* ---------- load group ---------- */
  useEffect(() => {
    fetchGroup()
      .then((res) => {
        console.log("members", res.data.members);   // <-- log members
        setGroup(res.data);
      })
      .catch((err) => console.error("Group fetch error:", err));
  }, []);

  /* ---------- load messages ---------- */
  useEffect(() => {
    if (!group) return;
    fetchMessages();
    const interval = setInterval(fetchMessages, 5000);
    return () => clearInterval(interval);
  }, [group]);

  const fetchMessages = async () => {
    try {
      const { data } = await api.get("/chat/messages/");
      setMessages(data);
    } catch (error) {
      console.error("Error fetching messages:", error);
    }
  };

  const handleSendMessage = async (e) => {
    e.preventDefault();
    if (!newMessage.trim()) return;

    setLoading(true);
    try {
      const { data } = await api.post("/chat/messages/", {
        content: newMessage,
      });
      setMessages((prev) => [...prev, data.message]);
      setNewMessage("");
      if (data.meeting) setPendingMeeting(data.meeting);
    } catch (error) {
      console.error("Error sending message:", error);
    } finally {
      setLoading(false);
    }
  };

  /* ---------- render ---------- */
  if (!group) {
    return (
      <div className="chat-container">
        <div className="loading">Loading group…</div>
      </div>
    );
  }

  return (
    <div className="chat-container">
      <div className="chat-header">
        <h2>Group: {group.name}</h2>
        <p>
          Members: {group.members?.map(m => m.username).join(', ') || 'None'}
        </p>
      </div>

      <div className="chat-messages">
        {messages.map((msg) => (
          <Message key={msg.id} message={msg} currentUser={user} />
        ))}
      </div>

      {pendingMeeting && (
        <MeetingScheduler
          meeting={pendingMeeting}
          onClose={() => setPendingMeeting(null)}
        />
      )}

      <form onSubmit={handleSendMessage} className="chat-input-form">
        <input
          type="text"
          value={newMessage}
          onChange={(e) => setNewMessage(e.target.value)}
          placeholder="Type a message..."
          disabled={loading}
        />
        <button type="submit" disabled={loading}>
          {loading ? "Sending…" : "Send"}
        </button>
      </form>
    </div>
  );
}

export default ChatInterface;