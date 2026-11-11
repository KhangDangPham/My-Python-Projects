"""Log parsing utilities."""
from datetime import datetime, timedelta
from collections import Counter
import re

from config import TIMESTAMP_FORMAT
from utils import log_execution


def parse_timestamps(timestamps, utc_offset_hours=0):
    """Parse timestamp strings and apply a UTC offset.

    The offset is a simple arithmetic adjustment added to the parsed
    (naive) datetimes. This is not timezone-aware conversion: no DST
    or timezone localisation is applied.

    Parameters
    ----------
    timestamps : list[str]
        Timestamp strings in "%Y-%m-%d %H:%M:%S" format.
    utc_offset_hours : int or float
        Hours to offset. Positive shifts forward, negative shifts back.

    Returns
    -------
    list[datetime]
        Parsed and offset datetime objects.

    Example
    -------
    >>> parse_timestamps(["2025-01-15 10:30:00"], utc_offset_hours=2)
    [datetime.datetime(2025, 1, 15, 12, 30)]
    """
    parsed_datetimes = []
    offset = timedelta(hours=utc_offset_hours)
    for timestamp in timestamps:
        dt = datetime.strptime(timestamp, TIMESTAMP_FORMAT)
        parsed_datetimes.append(dt + offset)
    return parsed_datetimes


def extract_error_codes(messages):
    """Extract error codes from log messages.

    Error codes follow the pattern: 2-4 uppercase letters, a hyphen,
    2-4 uppercase letters, a hyphen, then exactly two digits.

    Each message contains at most one error code. Messages without a
    matching code are skipped.

    Parameters
    ----------
    messages : list[str]
        Raw log message strings.

    Returns
    -------
    list[str]
        Error codes, in the order they appear.

    Example
    -------
    >>> extract_error_codes(["Disk failure [ERR-DISK-01]", "All clear"])
    ['ERR-DISK-01']
    >>> extract_error_codes(["lowercase err-conn-01", "no code"])
    []
    """
    pattern = re.compile(r'[A-Z]{2,4}-[A-Z]{2,4}-\d{2}')
    error_codes = []
    for message in messages:
        match = pattern.search(message)
        if match:
            error_codes.append(match.group(0))
    return error_codes


@log_execution
def count_by_severity(events, severity_field="severity"):
    """Count events grouped by a severity field.

    This function is decorated with @log_execution from utils.py.
    Do not remove the @log_execution decorator.

    Parameters
    ----------
    events : list[dict]
        Event records containing at least a severity field.
    severity_field : str
        Key name for the severity value in each dict.

    Returns
    -------
    Counter
        Counts keyed by severity level.

    Example
    -------
    >>> count_by_severity([{"severity": "ERROR"}, {"severity": "INFO"}])
    Counter({"ERROR": 1, "INFO": 1})
    """
    severity_counts = Counter(event[severity_field] for event in events if severity_field in event)
    return severity_counts
