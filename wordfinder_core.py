from datetime import timedelta


def format_timestamp(seconds: float, always_include_hours: bool = False, decimal_marker: str = '.'):
    """Convert seconds into a timestamp string."""
    if seconds < 0:
        raise ValueError("Non-negative timestamp expected")

    time_delta = timedelta(seconds=seconds)
    total_milliseconds = int(time_delta.total_seconds() * 1000)
    milliseconds = total_milliseconds % 1000
    hours, remainder = divmod(total_milliseconds, 3600000)
    minutes, seconds = divmod(remainder, 60000)
    seconds //= 1000

    hours_marker = f"{hours:02d}:" if always_include_hours or hours > 0 else ""
    return f"{hours_marker}{minutes:02d}:{seconds:02d}{decimal_marker}{milliseconds:03d}"


def format_segment_timestamp(seconds: float) -> str:
    """Format a segment start time as HH:MM:SS or MM:SS."""
    timestamp = format_timestamp(seconds, always_include_hours=True)
    hours, minutes, seconds_millis = timestamp.split(':')
    whole_seconds = seconds_millis.split('.')[0]
    if int(hours) > 0:
        return f"{hours}:{minutes}:{whole_seconds}"
    return f"{minutes}:{whole_seconds}"


def find_matching_segments(segments, words):
    """Return timestamped transcript segments containing any search term."""
    normalized_words = [word.strip().casefold() for word in words if word.strip()]
    matches = []

    for segment in segments:
        text = segment.get('text', '').strip()
        if any(word in text.casefold() for word in normalized_words):
            start_time = format_segment_timestamp(float(segment.get('start', 0)))
            matches.append(f"{start_time} - {text}\n\n")

    return matches
