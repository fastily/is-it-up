# is-it-up
[![Python 3.9+](https://upload.wikimedia.org/wikipedia/commons/4/4f/Blue_Python_3.9%2B_Shield_Badge.svg)](https://www.python.org)
[![License: GPL v3](https://upload.wikimedia.org/wikipedia/commons/8/86/GPL_v3_Blue_Badge.svg)](https://www.gnu.org/licenses/gpl-3.0.en.html)

A simple API for checking if a website/domain is online.  Useful for troubleshooting network issues (e.g. is it just me or is it down for everyone?).

## Usage
### GET `/check`
Takes a single URL parameter, `website` and queries it to see if it is up.  Retuns the http `status` code, and the time at which this domain was last queried as an iso 8601 timestamp.

* Responses are cached for 5m
* Only the domain will be queried.  If you pass a URL wtih a path, it will be truncated.
* Input is restricted to alpha-numeric characters, periods, and hyphens.

Example request:
```
/check?website=www.google.com
```

Example response:
```json
{"status":200,"last_checked":"2023-01-01T06:49:19+00:00"}
```

## Dependencies
* [Python](https://www.python.org) 3.9+
* [Redis](https://redis.io)

## Configuration
is-it-up can be configured via environment variables:
* `redis_host` - the port of the redis server to use.  defaults to `localhost`
* `redis_port` - the port of the redis server to use.  Defaults to `6379`
* `show_docs` - indicates if the `/docs` endpoint should be exposed via http redirect from `/`.  Disabling this causes a generic error to be shown when visiting `/`.  Defaults to `true`

## Development commands
```bash
# start
python -m is_it_up
```

## Production commands
```bash
# run w/ gunicorn
gunicorn -w 2 -k uvicorn.workers.UvicornWorker -b "0.0.0.0:8000" is_it_up.__main__:app
```