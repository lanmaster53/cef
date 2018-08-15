from cef import app

# gunicorn cef:app --worker-class gevent --bind 127.0.0.1:8888

if __name__ == '__main__':
    app.run(port=8888)
