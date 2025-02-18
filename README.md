# is-it-up
[![Python 3.11+](https://upload.wikimedia.org/wikipedia/commons/6/62/Blue_Python_3.11%2B_Shield_Badge.svg)](https://www.python.org)
[![License: GPL v3](https://upload.wikimedia.org/wikipedia/commons/8/86/GPL_v3_Blue_Badge.svg)](https://www.gnu.org/licenses/gpl-3.0.en.html)

A simple API for checking if a website/domain is online.  Useful for troubleshooting network issues (e.g. is it just me or is it down for everyone?).

## Usage
### GET `/check`
Takes a single URL parameter, `website` and queries it to see if it is up.  Retuns the http `status` code, the time at which this domain was last queried as an iso 8601 timestamp, and a boolean indiciating if this result was cached (i.e. whether someone else already made this request in the past 5m).

* Responses are cached for 5m
* Only the domain will be queried.  If you pass a URL wtih a path, it will be truncated.
* Input is restricted to alpha-numeric characters, periods, and hyphens.

Example request:
```
/check?website=www.google.com
```

Example response:
```json
{
    "status": 200,
    "last_checked": "2023-12-04T10:21:36+00:00",
    "cached": false
}
```

## Run
```bash
# start in development mode, visit http://127.0.0.1:8000 to view the web interface
python -m is_it_up

# run w/ gunicorn, accessible at localhost:8000
gunicorn -w 2 -k uvicorn.workers.UvicornWorker -b "0.0.0.0" is_it_up.__main__:app
```