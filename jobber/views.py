"""
jobber.views
~~~~~~~~~~~~

View declarations.

"""
from random import choice

from flask import render_template, abort
from flask import current_app as app

from jobber.models import Job
from jobber.core.search import Index
from jobber.core.forms import JobForm
from jobber.extensions import db
from jobber.view_helpers import (get_location_context,
                                 get_tag_context,
                                 populate_job,
                                 populate_form)


CREATE_OR_UPDATE_PROMPT = u'Great jobs, great people.'


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


@app.route('/search/')
@app.route('/')
def index():
    jobs = Job.query.filter_by(published=True).all()
    return render_template('index.html', jobs=jobs)


@app.route('/search/<query>')
def search(query):
    index = Index()
    jobs = []
    for hit in index.search(query):
        job = Job.query.get(hit['id'])
        # Make sure that we don't accidentally show an unpublished job that
        # happened to be in the search index.
        if job and job.published:
            jobs.append(job)
    return render_template('index.html', jobs=jobs, query=query)


@app.route('/create', methods=['GET', 'POST'])
def create():
    form = JobForm()

    if form.validate_on_submit():
        job = populate_job(form)
        db.session.commit()
        return render_template('jobs/submitted.html',
                               email=job.recruiter_email,
                               prompt=CREATE_OR_UPDATE_PROMPT)

    locations = get_location_context()
    tags = get_tag_context()

    return render_template('jobs/create_or_update.html',
                           form=form,
                           locations=locations,
                           tags=tags,
                           prompt=CREATE_OR_UPDATE_PROMPT)


@app.route('/edit/<int:job_id>/<token>', methods=['GET', 'POST'])
def edit(job_id, token):
    job = Job.query.filter_by(admin_token=token).first()

    if not (job and job_id == job.id):
        abort(404)

    form = populate_form(job)

    if form.validate_on_submit():
        job = populate_job(form, job=job)

        # An edited job is pending review so it needs to be unpublished.
        job.published = False

        db.session.commit()
        return render_template('jobs/submitted.html',
                               email=job.recruiter_email,
                               prompt=CREATE_OR_UPDATE_PROMPT)

    locations = get_location_context()
    tags = get_tag_context()

    return render_template('jobs/create_or_update.html',
                           form=form,
                           token=token,
                           locations=locations,
                           tags=tags,
                           prompt=CREATE_OR_UPDATE_PROMPT)


@app.route('/jobs/<int:job_id>/<company_slug>/<job_slug>')
def show(job_id, company_slug, job_slug):
    job = Job.query.get_or_404(job_id)
    if job.slug == job_slug and job.company.slug == company_slug:
        return render_template('jobs/show.html', job=job)
    abort(404)


@app.route('/preview', methods=['POST'])
def preview():
    form = JobForm()

    if form.validate_on_submit():
        job = populate_job(form)
        return render_template('jobs/show_chromeless.html', job=job)

    return 'Cannot render preview'


@app.route('/how')
def how():
    return 'how it works'
