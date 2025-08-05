import re
from datetime import datetime, timedelta
from dateutil import parser
import pytz

class MeetingIntentDetector:
    MEETING_KEYWORDS = [
        'meet', 'meeting', 'schedule', 'call', 'discussion', 'sync up',
        'catch up', 'connect', 'conference', 'appointment', 'gather'
    ]

    TIME_PATTERNS = [
        r'\b(today|tomorrow|day after tomorrow|yesterday)\b',
        r'\b(\d{1,2}[:.]\d{2}\s*(AM|PM|am|pm))\b',
        r'\b(\d{1,2}\s*(AM|PM|am|pm))\b',
        r'\b(between\s+\d{1,2}(?:[:.]\d{2})?\s*(?:AM|PM|am|pm)?\s+and\s+\d{1,2}(?:[:.]\d{2})?\s*(?:AM|PM|am|pm)?)\b',
        r'\b(on\s+\d{1,2}(st|nd|rd|th)?\s+\w+\s+\d{4})\b',
        r'\b(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})\b'
    ]

    @classmethod
    def detect_meeting_intent(cls, text):
        text_lower = text.lower()

        if re.search(r'\b(should have|should’ve|had|was|were|used to)\b.*\b(meet|meeting)\b', text_lower):
            return False

        return any(keyword in text_lower for keyword in cls.MEETING_KEYWORDS)

    @classmethod
    def extract_time_info(cls, text):
        times = []
        now = datetime.now(pytz.UTC)

        for pattern in cls.TIME_PATTERNS:
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                for match in matches:
                    if isinstance(match, tuple):
                        match = match[0]  # in case of group tuples
                    times.append(match.strip())

        # Handle relative terms
        if 'day after tomorrow' in text.lower():
            target_day = now + timedelta(days=2)
            times.append(target_day.strftime('%Y-%m-%d'))
        if 'tomorrow' in text.lower():
            target_day = now + timedelta(days=1)
            times.append(target_day.strftime('%Y-%m-%d'))
        if 'today' in text.lower():
            times.append(now.strftime('%Y-%m-%d'))

        return times

    @classmethod
    def process_message(cls, text):
        has_intent = cls.detect_meeting_intent(text)
        time_info = cls.extract_time_info(text) if has_intent else []

        return {
            'has_meeting_intent': has_intent,
            'time_info': time_info,
            'suggested_times': cls.suggest_times(time_info)
        }

    @classmethod
    def suggest_times(cls, extracted_times):
        now = datetime.now(pytz.UTC)
        slots = []

        # Parse dates from extracted time info
        parsed_date = None
        for token in extracted_times:
            try:
                parsed = parser.parse(token, fuzzy=True, dayfirst=True)
                if parsed > now:
                    parsed_date = parsed
                    break
            except Exception:
                continue

        if not parsed_date:
            # Fallback: next weekday
            parsed_date = now + timedelta(days=1)
            if parsed_date.weekday() >= 5:
                parsed_date += timedelta(days=(7 - parsed_date.weekday()))

        # Normalize to midnight
        parsed_date = parsed_date.replace(hour=0, minute=0, second=0, microsecond=0)

        # Suggest time slots for the detected date
        for hour in [9, 11, 14, 16]:
            slot = parsed_date + timedelta(hours=hour)
            slots.append(slot.isoformat())

        return slots