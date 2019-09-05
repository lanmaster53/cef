from cef import db, bcrypt
import binascii
import datetime

class BaseModel(db.Model):
    __abstract__ = True
    id = db.Column(db.Integer, primary_key=True)
    created = db.Column(db.DateTime, nullable=False, default=datetime.datetime.now)

    @property
    def created_as_string(self):
        return self.created.strftime("%Y-%m-%d %H:%M:%S")

    @property
    def _name(self):
        return self.__class__.__name__.lower()

class User(BaseModel):
    __tablename__ = 'users'
    username = db.Column(db.String, nullable=False, unique=True)
    password_hash = db.Column(db.String)

    @staticmethod
    def get_by_username(username):
        return User.query.filter_by(username=username).first()

    @property
    def password(self):
        raise AttributeError('password: write-only field')

    @password.setter
    def password(self, password):
        self.password_hash = bcrypt.generate_password_hash(binascii.hexlify(password.encode()))

    def check_password(self, password):
        return bcrypt.check_password_hash(self.password_hash, binascii.hexlify(password.encode()))

    def serialize(self):
        return {
            'id': self.id,
            'username': self.username,
        }

    def __repr__(self):
        return "<User '{}'>".format(self.email)

class Node(BaseModel):
    __tablename__ = 'nodes'
    fingerprint = db.Column(db.String, nullable=False, unique=True)
    ip_address = db.Column(db.String, nullable=False)
    target = db.Column(db.String, nullable=False)
    user_agent = db.Column(db.String, nullable=False)
    results = db.relationship('Result', backref=db.backref('node'), cascade="all, delete-orphan")

    @staticmethod
    def get_by_fingerprint(fp):
        return Node.query.filter_by(fingerprint=fp).first()

    def serialize(self):
        return {
            'id': self.id,
            'fingerprint': self.fingerprint,
            'ip_address': self.ip_address,
            'user_agent': self.user_agent,
        }

class Attack(BaseModel):
    __tablename__ = 'attacks'
    method = db.Column(db.String, nullable=False)
    url = db.Column(db.String, nullable=False)
    payload_exp = db.Column(db.String, nullable=False)
    content_type = db.Column(db.String, nullable=False)
    success = db.Column(db.String, nullable=False)
    fail = db.Column(db.String, nullable=False)
    results = db.relationship('Result', backref=db.backref('attack'), cascade="all, delete-orphan")

    def serialize(self):
        return {
            'id': self.id,
            'url': self.url,
        }

class Result(BaseModel):
    __tablename__ = 'results'
    attack_id = db.Column(db.Integer, db.ForeignKey('attacks.id'), nullable=False)
    node_id = db.Column(db.Integer, db.ForeignKey('nodes.id'), nullable=False)
    payload = db.Column(db.String, nullable=False)

    def serialize(self):
        return {
            'id': self.id,
            'created': self.created_as_string,
            'node_id': self.node_id,
            'payload': self.payload,
            'attack': Attack.query.get(self.attack_id).serialize(),
            'node': Node.query.get(self.node_id).serialize(),
        }