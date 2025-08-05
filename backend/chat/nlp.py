import re
from datetime import datetime, timedelta
from dateutil import parser
import pytz

class MeetingIntentDetector:
    MEETING_INTENT_PATTERNS = [
        r"\b(let's|lets|can we|could we|shall we|schedule|set up|arrange|organize|fix)\b.*\b(meet|meeting|call|discussion|sync up|connect|catch up)\b",
        r"\b(meet|meeting|call|discussion|connect|sync up|catch up)\b.*\b(now|today|tomorrow|next|this|at \d{1,2})\b",
        r"\b(plan|planning|try|want|need|like)\b.*\b(to )?(meet|schedule|connect|have a call)\b"
    ]

    NEGATIVE_INTENT_PATTERNS = [
        r"\b(should have|would have|could have|should’ve|could’ve|would’ve|wish|wished)\b.*\b(meeting|call|met)\b",
        r"\b(we had|had a meeting|was a call)\b"
    ]

    @classmethod
    def detect_meeting_intent(cls, text):
        text_lower = text.lower()
        for pattern in cls.NEGATIVE_INTENT_PATTERNS:
            if re.search(pattern, text_lower):
                return False
        for pattern in cls.MEETING_INTENT_PATTERNS:
            if re.search(pattern, text_lower):
                return True
        return False

    @classmethod
    def extract_time_info(cls, text):
        times = []
        normalized_date = None
        now = datetime.now(pytz.UTC)
        text_lower = text.lower()

        if "now" in text_lower:
            return [{
                "type": "exact",
                "date": now.strftime("%d/%m/%Y"),
                "time": now.strftime("%H:%M")
            }]

        if "day after tomorrow" in text_lower:
            date = now + timedelta(days=2)
            normalized_date = date.strftime("%d/%m/%Y")
        elif "tomorrow" in text_lower:
            date = now + timedelta(days=1)
            normalized_date = date.strftime("%d/%m/%Y")
        elif "today" in text_lower:
            normalized_date = now.strftime("%d/%m/%Y")

        date_list = []

        # Parse "10 August", "10 August 2025", etc.
        specific_date_match = re.search(r'\b(\d{1,2}(?:st|nd|rd|th)?\s+\w+(?:\s+\d{4})?)\b', text, re.IGNORECASE)
        if specific_date_match:
            try:
                parsed_date = parser.parse(specific_date_match.group(1), dayfirst=True)
                normalized_date = parsed_date.strftime("%d/%m/%Y")
            except:
                pass

        # Parse DD/MM/YYYY or DD-MM-YYYY
        slash_date_match = re.search(r'\b(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})\b', text)
        if slash_date_match:
            try:
                parsed_date = parser.parse(slash_date_match.group(1), dayfirst=True)
                normalized_date = parsed_date.strftime("%d/%m/%Y")
            except:
                pass

        # Time range
        range_match = re.search(
            r'between\s+(\d{1,2}(?::\d{2})?\s*(?:AM|PM|am|pm)?)\s+and\s+(\d{1,2}(?::\d{2})?\s*(?:AM|PM|am|pm)?)',
            text, re.IGNORECASE
        )
        if range_match:
            start_time = range_match.group(1)
            end_time = range_match.group(2)
            date_list.append({
                "type": "range",
                "date": normalized_date or now.strftime("%d/%m/%Y"),
                "start": start_time,
                "end": end_time
            })

        # Fixed time
        time_match = re.search(r'at\s+(\d{1,2}(?::\d{2})?\s*(?:AM|PM|am|pm))', text, re.IGNORECASE)
        if time_match:
            time_str = time_match.group(1)
            date_list.append({
                "type": "exact",
                "date": normalized_date or now.strftime("%d/%m/%Y"),
                "time": time_str
            })

        # Only date detected
        if not date_list and normalized_date:
            date_list.append({
                "type": "date-only",
                "date": normalized_date
            })

        # Print the detected date(s)
        for item in date_list:
            print("\n[INFO] Detected Date Block:", item)

        return date_list

    @classmethod
    def process_message(cls, text):
        has_intent = cls.detect_meeting_intent(text)
        time_info = cls.extract_time_info(text) if has_intent else []

        suggestions = cls.suggest_times(time_info) if has_intent else []

        # Print the final suggestions going to frontend
        print("📤 Final Suggested Slots to Frontend:", suggestions)

        return {
            'has_meeting_intent': has_intent,
            'time_info': time_info,
            'suggested_times': suggestions
        }

    @classmethod
    def suggest_times(cls, extracted_times):
        now = datetime.now(pytz.UTC)
        suggestions = []

        for time_block in extracted_times:
            if time_block['type'] == "exact":
                try:
                    dt = parser.parse(f"{time_block['date']} {time_block['time']}", dayfirst=True)
                    suggestions.append(dt.astimezone(pytz.UTC).isoformat())
                except:
                    continue

            elif time_block['type'] == "range":
                try:
                    dt = parser.parse(f"{time_block['date']} {time_block['start']}", dayfirst=True)
                    suggestions.append(dt.astimezone(pytz.UTC).isoformat())
                except:
                    continue

            elif time_block['type'] == "date-only":
                try:
                    base_date = parser.parse(time_block['date'], dayfirst=True)
                    for hour in [10, 11, 15]:
                        dt = base_date.replace(hour=hour, minute=0, second=0, microsecond=0)
                        suggestions.append(pytz.UTC.localize(dt).isoformat())
                except:
                    continue

        return suggestions
