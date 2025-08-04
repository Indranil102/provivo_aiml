// src/components/Meeting/MeetingScheduler.jsx
import React, { useState } from "react";
import api from "../../services/api";
import { useAuth } from "../../services/auth";   // to get current user
import "./Meeting.css";

function MeetingScheduler({ meeting, onClose }) {
  const { user } = useAuth();                    // current logged-in user
  const [selected, setSelected] = useState("");
  const [loading, setLoading] = useState(false);

  // 3 quick slots: +1h, +2h, +3h
  const slots = [
    new Date(Date.now() + 3600000),
    new Date(Date.now() + 7200000),
    new Date(Date.now() + 10800000),
  ];

  const handleSchedule = async () => {
    if (!selected) return;

    setLoading(true);
    try {
      // 1. schedule on backend
      await api.post("/chat/schedule/", {
        meeting_id: meeting.id,
        time: selected,
      });

      // 2. send chat message
      const dt = new Date(selected).toLocaleString();
      await api.post("/chat/messages/", {
        content: `Meeting scheduled at ${dt}`,
      });

      alert("Meeting scheduled!");
      onClose();
    } catch (err) {
      console.error(err);
      alert("Failed to schedule");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="meeting-modal-overlay">
      <div className="meeting-modal">
        <h3>Choose the best time for the meeting</h3>
        <p>{meeting.description}</p>

        {/* Time selector */}
        <select
          value={selected}
          onChange={(e) => setSelected(e.target.value)}
          className="time-picker"
        >
          <option value="" disabled>Pick a slot</option>
          {slots.map((dt) => (
            <option key={dt.toISOString()} value={dt.toISOString()}>
              {dt.toLocaleString()}
            </option>
          ))}
        </select>

        <div className="meeting-actions">
          <button onClick={handleSchedule} disabled={!selected || loading}>
            {loading ? "Scheduling…" : "Confirm"}
          </button>
          <button onClick={onClose} className="cancel-btn">
            Cancel
          </button>
        </div>
      </div>
    </div>
  );
}

export default MeetingScheduler;