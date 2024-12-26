"""Utility classes/functions for is_it_up"""

from http.cookiejar import CookieJar
from time import time


class NullCookieJar(CookieJar):
    """A CookieJar that rejects all cookies."""

    def extract_cookies(self, *_):
        """For extracting and saving cookies.  This implementation does nothing"""
        pass

    def set_cookie(self, _):
        """Normally for setting a cookie.  This implementation does nothing"""
        pass


class TokenBucketRateLimiter:
    """Basic implementation of a token bucket algorithim rate limiter"""

    def __init__(self, capacity: int = 128, fill_rate: int = 2):
        """Initializer, creates a new TokenBucketRateLimiter

        Args:
            capacity (int, optional): The maximum capacity of the bucket. Defaults to 128.
            fill_rate (int, optional): The rate at which the bucket refills with tokens, in seconds. Defaults to 2.
        """
        self._capacity = capacity  # Maximum tokens the bucket can hold
        self._fill_rate = fill_rate  # Tokens added per second
        self._tokens = capacity  # Current number of tokens in the bucket
        self._last_time = int(time())  # Last time tokens were added

    def is_allowed(self, tokens_requested: int = 1) -> bool:
        """Determines if whatever action the TokenBucketRateLimiter is being used to track can be performed

        Args:
            tokens_requested (int, optional): The number of tokens required to perform the action being tracked. Defaults to 1.

        Returns:
            bool: `True` if there are sufficient tokens available to perform the action being tracked.
        """
        self._tokens = min(self._capacity, self._tokens + ((current_time := int(time())) - self._last_time) * self._fill_rate)
        self._last_time = current_time

        if self._tokens >= tokens_requested:
            self._tokens -= tokens_requested
            return True
        return False
