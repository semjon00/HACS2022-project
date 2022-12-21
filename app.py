# Suboptimal design, may be insecure.
# This is a speedrun, we are not building a castle here.

import copy
import os
import random
import time

from flask import Flask, request, render_template, jsonify, url_for, send_from_directory

app = Flask(__name__)

# A better split would be across rooms
puppets = {}
puppeteers = {}
questions = {}

# ################

def read_questions():
    qq = open('./secret/questions.txt', 'r', encoding='utf8').read().split('========')
    cont = 1
    for q in qq:
        lines = [x.strip() for x in q.split('\n') if len(x.strip()) > 0]
        if len(lines) == 0:
            continue
        assert len(lines) == 5, f'Incorrect form, {cont} question'
        questions[cont] = {'question': str(cont) + '. ' + lines[0],
                           'options': [['A', 'B', 'C', 'D'][i-1] + '. ' + lines[i] for i in range(1, 5)]}
        cont += 1
    assert len(questions) > 0, f'No questions = no game'
    return


@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')


@app.route('/i_am_in', methods=['POST'])
def i_am_in():
    if len(questions) == 0:
        read_questions()
    if len(puppets) > 500 or len(puppeteers) > 500:  # fast and ugly patch against O(n^2) DoS
        puppets.clear()
        puppeteers.clear()

    name = request.form['name']
    room = request.form['room']
    if name != 'master':
        # Yes, people can pick exactly the same display names
        identity = 'h4kker_' + str(random.randint(0, int(1e12)))
        puppets[identity] = {'name': name, 'room': room, 'answers': {}, 'created': time.time()}
        return render_template('puppet.html', identity=identity, room=room)
    else:
        if room in puppeteers:
            return jsonify({'status': 'error'})
        identity = 'ma$ter_' + str(random.randint(0, int(1e12)))
        def_event = {'time': 0, 'type': 't', 'text': 'Waiting for the room master to start...'}
        puppeteers[room] = {'identity': identity, 'events': [def_event], 'created': time.time()}
        return render_template('puppeteer.html', identity=identity, room=room)


@app.route('/pool_for_puppets', methods=['GET'])
def pool_for_puppets():  # Horrible design
    """GET the last event of the room, expects: id and skip"""
    identity = request.args.get('identity')
    skip = int(request.args.get('skip'))

    room = puppets[identity]['room']
    if room not in puppeteers:
        return jsonify({'event_index': -1})
    event_index = len(puppeteers[room]['events'])
    if event_index == skip:
        return jsonify({'event_index': -1})
    event = puppeteers[room]['events'][event_index - 1]
    return jsonify({'event_index': event_index, 'event': event})


@app.route('/caac_puppet', methods=['POST'])
def caac_puppet():
    """Takes POST with puppet identity, number (question number) and a picked value (to a question, from 0 to 4)"""
    identity = request.json.get('identity')
    number = request.json.get('number')
    picked = request.json.get('picked')

    if number not in questions or picked not in range(4) or identity not in puppets:
        return jsonify({'status': 'error'})
    puppets[identity]['answers'][number] = picked
    return jsonify({'status': 'ok'})


def get_stats(room, question_n):
    if random.random() < 0.05:  # quick and dirty garbage collection
        for p in copy.copy(list(puppeteers.keys())):
            if puppeteers[p]['created'] + 24*60*60 < time.time():
                del puppeteers[p]
        for p in copy.copy(list(puppets.keys())):
            if puppets[p]['created'] + 24*60*60 < time.time():
                del puppets[p]

    stats = 4 * [0]
    for p in puppets.values():
        if p['room'] == room:  # Bad design
            if question_n in p['answers']:
                got = p['answers'][question_n]
                stats[got] += 1
    return stats


@app.route('/caac_puppeteer', methods=['POST'])
def caac_puppeteer():
    """Takes POST with identity (auth key), room (same as puppeteer_id) and a command (prompt)"""
    prompt = request.json.get('prompt').split(':')
    room = request.json.get('room')
    identity = request.json.get('identity')

    if identity != puppeteers[room]['identity'] or len(prompt) != 2:
        return jsonify({'status': 'error'})

    event = {}
    if prompt[0] in ['q', 'question']:
        q_number = int(prompt[1])
        if q_number not in questions:
            return jsonify({'status': 'error'})
        event['type'] = 'q'
        event['question'] = questions[q_number]['question']
        event['options'] = questions[q_number]['options']
        event['number'] = int(q_number)
    elif prompt[0] in ['p', 'picture', 'illustration', 'i', 'image']:
        event['type'] = 'p'
        event['display'] = True if prompt[1] in ['yes', 'y', '1', 'true'] else False  # unused
        if not event['display']:
            event['display'] = True
    elif prompt[0] in ['s', 'stat', 'stats', 'answers']:
        q_number = int(prompt[1])
        if q_number not in questions:
            return jsonify({'status': 'error'})
        event['type'] = 's'
        event['stats'] = get_stats(room, q_number)
        event['question'] = questions[q_number]['question']
        event['options'] = questions[q_number]['options']
    elif prompt[0] in ['e', 'exit', 'stop', 'no more misery']:
        event['type'] = 'e'
    elif prompt[0] in ['t', 'text']:
        event['type'] = 't'
        event['text'] = prompt[1]
    else:
        return jsonify({'status': 'error'})
    puppeteers[room]['events'] += [event]
    return jsonify({'status': 'ok'})


@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'),
                               'favicon.ico', mimetype='image/vnd.microsoft.icon')


if __name__ == '__main__':
    app.run()
