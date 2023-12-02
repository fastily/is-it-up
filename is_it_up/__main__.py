"""Main module, contains logic for web app"""

from datetime import datetime, timedelta, timezone
from typing import Any
from urllib.parse import urlparse
from uuid import uuid4

import uvicorn

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from httpx import AsyncClient, RequestError
from redis.asyncio import Redis

from .utils import NullCookieJar, Settings

_REPO_URL= "https://github.com/fastily/is-it-up"
_DESC = f"""\
[![License: GPL v3](https://upload.wikimedia.org/wikipedia/commons/8/86/GPL_v3_Blue_Badge.svg)](https://www.gnu.org/licenses/gpl-3.0.en.html)

A simple API for checking if a website/domain is online.

This is useful for instances when you can't acecss a website and want to check if there is a problem with your connection.

* To avoid clobbering hosts, responses are cached for 5m
* Only the domain will be queried.  If you pass a URL wtih a path, it will be truncated.
* Input is restricted to alpha-numeric characters, periods, and hyphens.

### Source
* [GitHub]({_REPO_URL})
"""
_DOCS_URL = "/docs"
_CACHE_TTL = 300
_UNREACHABLE_STATUS = -1
_REDIS_PREFIX = f"is-it-up-{uuid4()}"

settings = Settings()
cache: Redis = Redis(host=settings.redis_host, port=settings.redis_port)
client = AsyncClient(http2=True, cookies=NullCookieJar())

app = FastAPI(title="Is it Up?", description=_DESC, version="0.0.1", docs_url=_DOCS_URL if settings.show_docs else None, redoc_url=None)
app.add_middleware(CORSMiddleware, allow_origins=["https://ftools.toolforge.org"], allow_headers=["*"])


def _result_with_status(status: int, offset: int = 0) -> dict[str, Any]:
    """Convenience method, generates the output json for return to the user

    Args:
        status (int): The status code of the queried website to return
        offset (int, optional): The ttl (in seconds) for the key in redis, will be used to calc `last_checked` time. Defaults to 0.

    Returns:
        dict[str, Any]: _description_
    """
    n = datetime.now(timezone.utc).replace(microsecond=0)
    return {"status": status, "last_checked": ((n - timedelta(seconds=_CACHE_TTL-offset)) if offset else n).isoformat()}


@app.on_event("shutdown")
async def shutdown_event() -> None:
    """Closes the redis and httpx client connections"""
    await cache.close()
    await client.aclose()


@app.get("/", include_in_schema=False)
async def main():
    """Index, either shows help or redirects to docs, depending on env settings"""
    return RedirectResponse(_DOCS_URL) if settings.show_docs else {"visit_for_help": _REPO_URL}


@app.get("/check")
async def check_website(website: str = Query(max_length=100, pattern=r"[A-Za-z0-9\-\.]+")) -> dict[str, Any]:
    """Main endpoint logic for checking if a website is online.  Uses redis to cache results.

    Args:
        website (str, optional): The website to check. Defaults to Query(max_length=100, regex=r"[A-Za-z0-9\-\.]+").

    Returns:
        dict[str, Any]: The result, containing info about whether the website was reachable.
    """
    o = urlparse(website)
    if not (o.netloc or o.path) or "." not in website:
        raise HTTPException(400, "input website is malformed")

    u = f"{o.scheme or 'https'}://{o.netloc or o.path}"
    redis_key = f"{_REDIS_PREFIX}-{u}"
    if (status := await cache.get(redis_key)) and (ttl := await cache.ttl(redis_key)) > 0:
        return _result_with_status(int(status.decode()), ttl)

    try:
        async with client.stream("GET", u, headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36"}) as response:
            await cache.set(redis_key, response.status_code, _CACHE_TTL)
            return _result_with_status(response.status_code)
    except RequestError:
        await cache.set(redis_key, _UNREACHABLE_STATUS, _CACHE_TTL)
        return _result_with_status(_UNREACHABLE_STATUS)
    except:
        raise HTTPException(500, "Server error, unable to reach target website")


if __name__ == "__main__":
    uvicorn.run("is_it_up.__main__:app", reload=True)
