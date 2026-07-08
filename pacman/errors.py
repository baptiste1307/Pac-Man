from pathlib import Path
import inspect
import traceback


def format_error(message: object, file: str, line: int) -> str:
    """Format an error message with its source file and line."""
    return f"Error ({file}, line {line}): {message}"


def format_current_error(message: object) -> str:
    """Format an error at the caller's current source location."""
    frame = inspect.currentframe()
    caller = frame.f_back if frame is not None else None

    if caller is None:
        return f"Error (unknown, line 0): {message}"

    file = Path(caller.f_code.co_filename).as_posix()
    return format_error(message, file, caller.f_lineno)


def format_exception_error(error: BaseException) -> str:
    """Format an exception using the last frame of its traceback."""
    trace = traceback.extract_tb(error.__traceback__)

    if not trace:
        return f"Error (unknown, line 0): {error}"

    last_frame = trace[-1]
    file = Path(last_frame.filename).as_posix()
    return format_error(error, file, last_frame.lineno)
