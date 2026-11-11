"""Event processing classes."""
import pandas as pd
from config import SEVERITY_LEVELS


class EventProcessor:
    """Filter server events by minimum severity level."""

    def __init__(self, events, min_severity="INFO"):
        self.events = events
        self.min_severity = min_severity
        self._processed = None

    def process(self):
        """Filter events at or above min_severity, sorted by timestamp."""
        threshold = SEVERITY_LEVELS.get(self.min_severity, 0)
        self._processed = [
            e for e in self.events
            if SEVERITY_LEVELS.get(e.get("severity", ""), 0) >= threshold
        ]
        self._processed.sort(key=lambda e: e.get("timestamp", ""))
        return self._processed


class AlertProcessor(EventProcessor):
    """Process events and flag alerts."""

    def __init__(self, events, min_severity="WARNING"):
        super().__init__(events, min_severity)

    def process(self):
        filtered = super().process()
        for event in filtered:
            event["is_alert"] = event.get("severity", "") in ("ERROR", "CRITICAL")
        return filtered


class BatchProcessor(EventProcessor):
    """Process events loaded from multiple CSV log files.

    You may assume each CSV file is well-formed: correct columns,
    valid severity values, and no missing fields.

    Parameters
    ----------
    file_paths : list[str]
        Paths to CSV log files.
    min_severity : str
        Minimum severity to include. Default is "INFO".

    The process() method should:
    1. Load each CSV file using pd.read_csv.
    2. Convert each DataFrame to a list of dicts.
    3. Combine all events into self.events.
    4. Filter to events at or above min_severity.
    5. Sort the filtered events by severity descending (most severe
       first), then by timestamp ascending (earliest first) within
       each severity level.
    Return the filtered, sorted list.

    Also implement:
    - __len__: return the number of processed events. Return 0 if
      process() has not yet been called.
    - __repr__: return a string in the format
      "BatchProcessor(<n> files, <m> events processed)"
      where <n> is the number of file paths and <m> is the number of
      processed events (0 if not yet processed).
    """
    def __init__(self, file_paths, min_severity="INFO"):
        self.file_paths = file_paths
        self.min_severity = min_severity
        self.events = []
        self._processed = None

    def process(self):
        """Load and combine events from multiple files, filter, and sort."""
        combined_events = []
        for file_path in self.file_paths:
            df = pd.read_csv(file_path)
            combined_events.extend(df.to_dict(orient="records"))

        self.events = combined_events
        threshold = SEVERITY_LEVELS.get(self.min_severity, 0)
        filtered_events = [e for e in self.events if SEVERITY_LEVELS.get(e.get("severity", ""), 0) >= threshold]
        
        filtered_events.sort(key=lambda e: (-SEVERITY_LEVELS.get(e.get("severity", ""), 0), e.get("timestamp", "")))
        self._processed = filtered_events
        return self._processed

    def __len__(self):
        if self._processed is None:
            return 0
        return len(self._processed)

    def __repr__(self):
        n = len(self.file_paths)                                          # number of file paths
        m = len(self._processed) if self._processed is not None else 0    # number of processed events
        return f"BatchProcessor({n} files, {m} events processed)"
