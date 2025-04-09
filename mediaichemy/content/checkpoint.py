import asyncio
from functools import wraps
import logging

# Configure logger
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


def checkpoint(state):
    """
    A decorator to update the state of the content object before and after
    the execution of a method, supporting both sync and async functions.

    If the checkpoint has already been reached, the method is skipped.

    :param state: str
        The name of the state to update in the content object.
    """
    def decorator(func):
        @wraps(func)
        async def async_handler(content, *args, **kwargs):
            return await _handle_checkpoint(func, content, state, *args, **kwargs)

        @wraps(func)
        def sync_handler(content, *args, **kwargs):
            return _handle_checkpoint(func, content, state, *args, **kwargs)

        # Return the appropriate handler based on whether the function is a coroutine
        return async_handler if asyncio.iscoroutinefunction(func) else sync_handler

    return decorator


async def _handle_checkpoint(func, content, state, *args, **kwargs):
    """
    Handle the checkpoint logic for both sync and async functions.

    :param func: callable
        The function being decorated.
    :param content: object
        The content object with a `state` and `STATES` attribute.
    :param state: str
        The name of the state to update.
    :return: Any
        The result of the function execution or the return value of the skipped state.
    """
    # Check if the checkpoint has already been reached
    has_checkpoint_been_reached = content.STATES[content.state][0] >= content.STATES[state][0]
    if has_checkpoint_been_reached:
        logger.warning(f"Skipping {func.__name__}: Checkpoint '{state}' has already been reached.")
        return content.STATES[state][1]

    # Execute the method
    if asyncio.iscoroutinefunction(func):
        result = await func(content, *args, **kwargs)
    else:
        result = func(content, *args, **kwargs)

    # Update the state after the method execution
    content.state = state
    logger.info(f"Content state updated: {content.state}")
    _save_state(content)
    return result


def _save_state(content):
    """
    Save the current state of the content object to a simple text file.

    :param content: object
        The content object with a `state` attribute.
    """
    state_file = content.dir + "/.state"
    try:
        with open(state_file, "w") as file:
            file.write(content.state)  # Write the current state as plain text
        logger.info(f"State saved to {state_file}: {content.state}")
    except Exception as e:
        logger.error(f"Failed to save state to {state_file}: {e}")
