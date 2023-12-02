"""Utility classes/functions for is_it_up"""

from http.cookiejar import CookieJar

from pydantic_settings import BaseSettings


class NullCookieJar(CookieJar):
    """A CookieJar that rejects all cookies."""

    def extract_cookies(self, *_):
        """For extracting and saving cookies.  This implementation does nothing"""
        pass

    def set_cookie(self, _):
        """Normally for setting a cookie.  This implementation does nothing"""
        pass


class Settings(BaseSettings):
    """Represents the settings obtained via environment variables"""
    redis_host: str = "localhost"
    redis_port: int = 6379
    show_docs: bool = True
