from flask import Flask
from flask_bcrypt import Bcrypt
from flask_sqlalchemy import SQLAlchemy
from queue import Queue
import os
import redis

basedir = os.path.abspath(os.path.dirname(__file__))

# configuration
DEBUG = True
SECRET_KEY = 'dosentmatter'
SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'cef.db')
SQLALCHEMY_TRACK_MODIFICATIONS = False
FILES_DIR = '/path/to/cef/lists/'

app = Flask(__name__)
app.config.from_object(__name__)
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)

# streaming setup

rs = redis.StrictRedis(
    host='localhost',
    port=6379,
    db=0,
    charset='utf-8',
    decode_responses=True,
)

import cef.views

# manage

'''
import cef
cef.drop_db()
cef.init_db()
cef.pop_db()
'''

def init_db():
    db.create_all()
    print('Database initialized.')

def pop_db():
    # seed a user
    from cef.models import User
    u = User(
        username='demo',
        password='password'
    )
    db.session.add(u)
    db.session.commit()
    print('Database populated.')

def drop_db():
    db.drop_all()
    print('Database dropped.')
