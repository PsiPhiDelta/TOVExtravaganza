"""
Timeout utility for long-running TOV calculations
"""
import threading
import functools


class TimeoutError(Exception):
    """Raised when a function call times out"""
    pass


def timeout(seconds):
    """
    Decorator to add a timeout to a function call.
    
    Parameters:
    -----------
    seconds : float or None
        Maximum time allowed for function execution. If None, no timeout is applied.
        
    Returns:
    --------
    Decorated function that raises TimeoutError if it exceeds the time limit.
    
    Example:
    --------
    @timeout(60)
    def slow_function():
        # Do something that might take a long time
        pass
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            if seconds is None or seconds <= 0:
                # No timeout, run normally
                return func(*args, **kwargs)
            
            result = [None]
            exception = [None]
            
            def target():
                try:
                    result[0] = func(*args, **kwargs)
                except Exception as e:
                    exception[0] = e
            
            thread = threading.Thread(target=target)
            thread.daemon = True
            thread.start()
            thread.join(timeout=seconds)
            
            if thread.is_alive():
                # Thread is still running, timeout occurred
                raise TimeoutError(f"Function '{func.__name__}' timed out after {seconds} seconds")
            
            if exception[0] is not None:
                raise exception[0]
            
            return result[0]
        
        return wrapper
    return decorator

