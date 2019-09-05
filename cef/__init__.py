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
FILES_DIR = '/Users/lanmaster/Development/Repositories/cef/lists/'

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
        username='tim',
        password='password'
    )
    db.session.add(u)
    db.session.commit()
    # seed an attack
    from cef.models import Attack
    a = Attack(
        method='POST',
        url='https://cody-juiceshop.herokuapp.com/rest/user/login',
        payload_exp="json.dumps({'email':u,'password':p})",
        content_type='application/json',
        success='"token":',
        fail='Invalid email or password.',
    )
    db.session.add(a)
    db.session.commit()
    print('Database populated.')

def drop_db():
    db.drop_all()
    print('Database dropped.')
