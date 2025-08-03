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
        r'\b(today|tomorrow|yesterday)\b',
        r'\b(\d{1,2}:\d{2}\s*(?:AM|PM|am|pm)?)\b',
        r'\b(\d{1,2}\s*(?:AM|PM|am|pm))\b',
        r'\b(next\s+\w+|this\s+\w+|last\s+\w+)\b',
        r'\b(\d{1,2}\/\d{1,2}\/\d{2,4})\b',
        r'\b(\d{1,2}-\d{1,2}-\d{2,4})\b'
    ]
    
    @classmethod
    def detect_meeting_intent(cls, text):
        text_lower = text.lower()
        return any(keyword in text_lower for keyword in cls.MEETING_KEYWORDS)
    
    @classmethod
    def extract_time_info(cls, text):
        times = []
        for pattern in cls.TIME_PATTERNS:
            matches = re.findall(pattern, text, re.IGNORECASE)
            times.extend(matches)
        
        # Try to parse relative times
        now = datetime.now(pytz.UTC)
        
        if 'today' in text.lower():
            times.append(now.strftime('%Y-%m-%d'))
        elif 'tomorrow' in text.lower():
            tomorrow = now + timedelta(days=1)
            times.append(tomorrow.strftime('%Y-%m-%d'))
        
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
        suggestions = []
        now = datetime.now(pytz.UTC)
        
        if not extracted_times:
            # Suggest next business day
            next_day = now + timedelta(days=1)
            if next_day.weekday() >= 5:  # Weekend
                next_day += timedelta(days=(7 - next_day.weekday()))
            
            for hour in [9, 10, 14, 15]:
                suggested = next_day.replace(hour=hour, minute=0, second=0)
                suggestions.append(suggested.isoformat())
        
        return suggestions