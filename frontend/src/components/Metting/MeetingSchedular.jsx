import React, { useState, useEffect } from "react";
import api from "../../services/api";
import { useAuth } from "../../services/auth";
import "./Meeting.css";

function MeetingScheduler({ meeting, onClose }) {
  const { user } = useAuth();
  const [selected, setSelected] = useState("");
  const [loading, setLoading] = useState(false);

  
  useEffect(() => {
    console.log("[MeetingScheduler] Full meeting object from backend:", meeting);
  }, [meeting]);


  const slots = Array.isArray(meeting?.suggested_times)
    ? meeting.suggested_times.map((iso) => new Date(iso))
    : [];


  useEffect(() => {
    console.log("[MeetingScheduler] Extracted slots from NLP:", slots);
  }, [slots]);

  const handleSchedule = async () => {
    if (!selected) return;

    setLoading(true);
    try {
      await api.post("/chat/schedule/", {
        meeting_id: meeting.id,
        time: selected,
      });

      const dtObj = new Date(selected);
      const formattedDate = dtObj.toLocaleDateString(undefined, {
        weekday: "long",
        year: "numeric",
        month: "long",
        day: "numeric",
      });
      const formattedTime = dtObj.toLocaleTimeString(undefined, {
        hour: "2-digit",
        minute: "2-digit",
      });

     
      const content = `📅 *Meeting Scheduled*\n🗓️ ${formattedDate} at ${formattedTime}\n👤 Created by: ${meeting.creator?.username}\n🔗 (https://meet.google.com/xvp-mfko-qwz)`;

      await api.post("/chat/messages/", {
        content,
      });

      alert("Meeting scheduled!");
      onClose();
    } catch (err) {
      console.error("[MeetingScheduler] Scheduling error:", err);
      alert("Failed to schedule meeting");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="meeting-modal-overlay">
      <div className="meeting-modal">
        <h3>Choose a meeting time</h3>
        <p>{meeting.description}</p>

        {slots.length > 0 ? (
          <select
            value={selected}
            onChange={(e) => setSelected(e.target.value)}
            className="time-picker"
          >
            <option value="" disabled>
              Pick a slot
            </option>
            {slots.map((dt) => (
              <option key={dt.toISOString()} value={dt.toISOString()}>
                {dt.toLocaleString()}
              </option>
            ))}
          </select>
        ) : (
          <p className="no-slots">⚠️ No suggested times available.</p>
        )}

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
