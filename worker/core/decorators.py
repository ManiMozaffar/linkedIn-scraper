import asyncio
import threading
import random
from typing import Callable, Any
from functools import wraps

import loguru


class add_task:
    def __init__(self, level=0):
        self.level = level

    def __call__(self, func):
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)

        wrapper._task_info = {
            'level': self.level,
            'func': func,
        }
        return wrapper


def async_timeout(timeout: float):
    def decorator(func: Callable) -> Callable:
        async def wrapper(*args: Any, **kwargs: Any) -> Any:
            try:
                return await asyncio.wait_for(func(*args, **kwargs), timeout)
            except asyncio.TimeoutError:
                raise TimeoutError(
                    f"Function '{func.__name__}' exceeded {timeout} seconds."
                )
        return wrapper
    return decorator


def get_unique_object(func: Callable):
    """
    This decorator maintains a list of used objects and ensures that the
    wrapped function. returns a unique object each time it is called until
    all objects have been used. Once all objects have been used,
    the list of used objects is cleared and the process starts again.

    Args:
        func (callable): A function that returns a list of objects.

    Returns:
        Callable: A wrapped function that returns a tuple containing a unique
            object from the list and the list of used objects.
    """
    used_objects = set()

    @wraps(func)
    def wrapper(*args, **kwargs):
        nonlocal used_objects
        with threading.Lock():
            objects = func(*args, **kwargs)
            unused_objects = list(set(objects) - used_objects)
            if len(used_objects) != len(objects) and (
                len(unused_objects) > 0
            ):
                result = random.choice(unused_objects)

                used_objects.add(result)
                loguru.logger.info(
                    f"Total Objects Left: {len(unused_objects)-1}"
                )
                return result
            else:
                used_objects.clear()
                loguru.logger.info(
                    "Total Objects Reinitialized"
                )
                return wrapper(*args, **kwargs)

    return wrapper
