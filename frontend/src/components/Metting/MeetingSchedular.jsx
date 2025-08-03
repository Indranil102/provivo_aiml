import React, { useState } from "react";
import api from "../../services/api";
import "./Meeting.css";

function MeetingScheduler({ meeting, onClose }) {
  const [selectedTime, setSelectedTime] = useState("");
  const [loading, setLoading] = useState(false);

  const handleSchedule = async () => {
    if (!selectedTime) return;

    setLoading(true);
    try {
      await api.post("/chat/schedule/", {
        meeting_id: meeting.id,
        time: selectedTime,
      });

      alert("Meeting scheduled successfully!");
      onClose();
    } catch (error) {
      console.error("Error scheduling meeting:", error);
      alert("Failed to schedule meeting");
    } finally {
      setLoading(false);
    }
  };

  const suggestedTimes = [
    new Date(Date.now() + 3600000).toISOString(),
    new Date(Date.now() + 7200000).toISOString(),
    new Date(Date.now() + 10800000).toISOString(),
  ];

  return (
    <div className="meeting-modal-overlay">
      <div className="meeting-modal">
        <h3>Schedule Meeting</h3>
        <p>{meeting.description}</p>

        <div className="time-selector">
          <label>Select time:</label>
          <select
            value={selectedTime}
            onChange={(e) => setSelectedTime(e.target.value)}
          >
            <option value="">Choose a time...</option>
            {suggestedTimes.map((time) => (
              <option key={time} value={time}>
                {new Date(time).toLocaleString()}
              </option>
            ))}
          </select>
        </div>

        <div className="meeting-actions">
          <button onClick={handleSchedule} disabled={!selectedTime || loading}>
            {loading ? "Scheduling..." : "Schedule"}
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
