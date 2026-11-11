"""Pipeline summary utilities."""
from dataclasses import dataclass
from collections import Counter
from pathlib import Path
import pandas as pd

@dataclass
class PipelineResult:
    """Dataclass to store pipeline results"""
    processed_events: list
    severity_counts: Counter

def run_pipeline(file_path):
    """Run the log processing pipeline on a CSV log file.
    
    Parameters
    ----------
    file_path: str or Path
        Path to the CSV log file.

    Returns
    -------
    PipelineResult
        Contains the list of event dicts and a Counter of severity levels.

    Raises
    ------
    FileNotFoundError
        If the file does not exist.
    ValueError
        If the file contains no rows.
    """
    path = Path(file_path)
    if not path.is_file():
        raise FileNotFoundError(f"Log file not found: {file_path}")

    df = pd.read_csv(path)

    if df.empty:
        raise ValueError(f"Log file is empty (contains no rows): {file_path}")

    processed_events = df.to_dict(orient="records")
    severity_counts = Counter(event.get("severity") for event in processed_events if "severity" in event)
    
    return PipelineResult(processed_events=processed_events, severity_counts=severity_counts)
