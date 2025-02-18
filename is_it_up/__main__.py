"""Main module, contains logic for web app"""

from datetime import datetime, timezone
from random import choice
from typing import Any
from urllib.parse import urlparse

import uvicorn

from cachetools import TTLCache
from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import RedirectResponse
from httpx import AsyncClient, RequestError
from spawn_user_agent.user_agent import SpawnUserAgent

from .utils import NullCookieJar, TokenBucketRateLimiter

_REPO_URL = "https://github.com/fastily/is-it-up"
_DESC = f"""\
[![License: GPL v3](https://upload.wikimedia.org/wikipedia/commons/8/86/GPL_v3_Blue_Badge.svg)](https://www.gnu.org/licenses/gpl-3.0.en.html)

A simple API for checking if a website/domain is online.

This is useful for instances when you can't access a website and want to check if there is a problem with your connection.

* To avoid clobbering hosts, responses are cached for 5m
* Only the domain will be queried.  If you pass a URL wtih a path, it will be truncated.
* Input is restricted to alpha-numeric characters, periods, and hyphens.

### Source
* [GitHub]({_REPO_URL})
"""
_DOCS_URL = "/docs"
_UNREACHABLE_STATUS = -1
_USER_AGENTS = SpawnUserAgent.generate_all()

client = AsyncClient(http2=True, cookies=NullCookieJar())
cache = TTLCache(2 ^ 16, 60*5)
limiter = TokenBucketRateLimiter()

app = FastAPI(title="Is it Up?", description=_DESC, version="0.0.1", debug=True)


def _now_timestamp() -> str:
    """Convenience method, gets the current date & time in the iso8061 format

    Returns:
        str: The current date & time in the iso8061 format
    """
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def _result_with_status(status: int, last_checked: str, cached: bool = False) -> dict[str, Any]:
    """Convenience method, generates the output json for the user

    Args:
        status (int): The status code of the queried website
        last_checked (str): The timestamp at which the website was last checked
        cached (bool, optional): Indicates if this is a cached result or not. Defaults to False.

    Returns:
        dict[str, Any]: The output json to send to the user
    """
    return {"status": status, "last_checked": last_checked, "cached": cached}


@app.get("/", include_in_schema=False)
async def main() -> RedirectResponse:
    """Index, redirects to docs

    Returns:
        RedirectResponse: A redirect to the `/docs` endpoint
    """
    return RedirectResponse(_DOCS_URL)


@app.get("/health", include_in_schema=False)
async def health() -> dict:
    """Health check endpoint which returns an empty body 200

    Returns:
        dict: An empty json object
    """
    return {}


@app.get("/check")
async def check_website(website: str = Query(max_length=128, pattern=r"[A-Za-z0-9.-]+")) -> dict[str, Any]:
    """Main endpoint logic for checking if a website is online.

    Args:
        website (str, optional): The website to check. Defaults to Query(max_length=100, regex=r"[A-Za-z0-9.-]+").

    Returns:
        dict[str, Any]: The result, containing info about whether the website was reachable.
    """
    o = urlparse(website)
    if not (o.netloc or o.path) or "." not in website:
        raise HTTPException(400, "input website is malformed")

    if (u := f"{o.scheme or 'https'}://{o.netloc or o.path}") in cache:
        return _result_with_status(*cache.get(u), True)

    if not limiter.is_allowed():
        raise HTTPException(429)

    try:
        async with client.stream("GET", u, headers={"User-Agent": choice(_USER_AGENTS)}) as response:
            cache[u] = (response.status_code, _now_timestamp())
            return _result_with_status(*cache[u])
    except RequestError:
        cache[u] = (_UNREACHABLE_STATUS, _now_timestamp())
        return _result_with_status(*cache[u])
    except:
        raise HTTPException(500, "Server error, unable to reach target website")


if __name__ == "__main__":
    uvicorn.run("is_it_up.__main__:app", reload=True)
