from cef import db
import datetime

class BaseModel(db.Model):
    __abstract__ = True
    id = db.Column(db.Integer, primary_key=True)
    created = db.Column(db.DateTime, nullable=False, default=datetime.datetime.now)

    @property
    def _name(self):
        return self.__class__.__name__.lower()

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

class Attack(BaseModel):
    __tablename__ = 'attacks'
    method = db.Column(db.String, nullable=False)
    url = db.Column(db.String, nullable=False)
    payload_exp = db.Column(db.String, nullable=False)
    content_type = db.Column(db.String, nullable=False)
    success = db.Column(db.String, nullable=False)
    fail = db.Column(db.String, nullable=False)
    results = db.relationship('Result', backref=db.backref('attack'), cascade="all, delete-orphan")

class Result(BaseModel):
    __tablename__ = 'results'
    attack_id = db.Column(db.Integer, db.ForeignKey('attacks.id'), nullable=False)
    node_id = db.Column(db.Integer, db.ForeignKey('nodes.id'), nullable=False)
    payload = db.Column(db.String, nullable=False)
