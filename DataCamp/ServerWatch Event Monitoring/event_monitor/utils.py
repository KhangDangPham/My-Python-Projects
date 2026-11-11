"""Shared utilities for the event monitoring system."""
import time
import functools


def log_execution(func):
    """Decorator that tracks execution time and call count.

    After each call, the decorated function will have two attributes:
        - last_execution_time (float): seconds taken by the most recent call
        - call_count (int): total number of times the function has been called
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        wrapper.last_execution_time = time.time() - start
        wrapper.call_count = getattr(wrapper, "call_count", 0) + 1
        return result
    wrapper.last_execution_time = 0.0
    wrapper.call_count = 0
    return wrapper
