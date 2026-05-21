import functools
import logging
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
from circuitbreaker import circuit

logger = logging.getLogger(__name__)

def retry_policy():
    return retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type(Exception),
        before_sleep=lambda retry_state: logger.warning(
            f"Retry {retry_state.attempt_number} for {retry_state.fn.__name__} "
            f"after error: {retry_state.outcome.exception()}"
        )
    )

def resilient_call(func):
    @functools.wraps(func)
    @circuit(failure_threshold=3, recovery_timeout=30)
    @retry_policy()
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)
    return wrapper