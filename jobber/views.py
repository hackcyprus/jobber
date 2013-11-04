"""
jobber.views
~~~~~~~~~~~~

View declarations.

"""
from random import choice
from flask import render_template

from jobber.app import app
from jobber.models import Job


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


@app.context_processor
def inject_swag():
    prompt = choice(PROMPTS)
    position = choice(EXAMPLE_POSITIONS)
    return dict(prompt=prompt, position=position)


@app.route('/')
def index():
    jobs = Job.query.all()
    return render_template('index.html', jobs=jobs)


@app.route('/new')
def new():
    return 'new job'


@app.route('/how')
def how():
    return 'how it works'


@app.route('/j/<int:job_id>/<job_slug>')
def view(job_id, job_slug):
    job = Job.query.get_or_404(job_id)
    return render_template('job.html', job=job)
