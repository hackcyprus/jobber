"""
jobber.views
~~~~~~~~~~~~

View declarations.

"""
from random import choice
from flask import render_template
from jobber.app import app


PROMPTS = [
    u"What's your cup of tech?",
    u'Disruption is the new black.',
    u'Always not non-techie.',
    u'Software is eating the world.',
    u'Everybody chill, we got solder.'
]

EXAMPLE_POSITIONS = [
    u'web developer',
    u'engineer',
    u'python developer',
    u'system administrator',
    u'c#',
    u'.NET developer'
]


@app.route('/')
def index():
    prompt = choice(PROMPTS)
    position = choice(EXAMPLE_POSITIONS)
    return render_template('index.html', prompt=prompt, position=position)


@app.route('/all')
def all():
    return 'all jobs'


@app.route('/new')
def new():
    return 'new job'


@app.route('/j/([0-9]+)/(.+)')
def view():
    return 'view job'