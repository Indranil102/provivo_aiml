
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

  useEffect(() => {
    fetchGroup()
      .then((res) => {
        console.log("Group members:", res.data.members);
        setGroup(res.data);
      })
      .catch((err) => console.error("Group fetch error:", err));
  }, []);

  useEffect(() => {
    if (!group) return;
    fetchMessages();
    const interval = setInterval(fetchMessages, 5000); // Polling every 5s
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

      const newMsg = data.message || data; 
      if (!newMsg || !newMsg.id) {
        console.error("Invalid message format from API:", data);
      } else {
        setMessages((prev) => [...prev, newMsg]);
      }

      if (data.meeting) {
        setPendingMeeting(data.meeting);
      }

      setNewMessage(""); 
    } catch (error) {
      console.error("Error sending message:", error);
    } finally {
      setLoading(false);
    }
  };

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
