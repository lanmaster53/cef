# CORS Exploitation Framework (CEF)

This was thrown together. Will update later.

## Setup

1. Install Redis and Python 3.
2. Clone this repo.
3. Install the dependencies using `pip`.
    * `pip install -r requirements`
4. Set the `FILES_DIR` configuration item in `cef/__init__.py` to a directory that contains lists of credentials.
    * Credentials \*MUST\* be in `username:password` format.
5. Initialize the database in a Python interactive shell.

        import cef
        cef.init_db()

6. Launch Redis.
    * `$ redis-server`
7. Launch CEF.
    * `$ gunicorn cef:app --worker-class gevent --bind 127.0.0.1:8888`
8. Visit http://127.0.0.1:8888/dashboard.
