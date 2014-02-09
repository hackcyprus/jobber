"""
jobber.views
~~~~~~~~~~~~

View declarations.

"""
from random import choice

from flask import render_template, abort, redirect, url_for, session
from flask import current_app as app

from jobber.core.models import Job
from jobber.core.search import Index
from jobber.core.forms import JobForm
from jobber.extensions import db
from jobber.functions import send_instructory_email, send_admin_review_email
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
    query = Job.query.filter_by(published=True).order_by(Job.created.desc())
    return render_template('index.html', jobs=query.all())


@app.route('/search/<query>')
def search(query):
    index = Index()
    jobs = []

    for hit in index.search(query, sort=('created', 'desc')):
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

        db.session.add(job)
        db.session.commit()

        send_instructory_email(job)
        send_admin_review_email(job)

        app.logger.info("Job ({}) was successfully created.".format(job.id))

        session['created_email'] = job.recruiter_email
        return redirect(url_for('created'))

    locations = get_location_context()
    tags = get_tag_context()

    return render_template('jobs/create_or_edit.html',
                           form=form,
                           locations=locations,
                           tags=tags,
                           prompt=CREATE_OR_UPDATE_PROMPT)


@app.route('/created')
def created():
    email = session.pop('created_email', None)
    if not email:
        abort(404)
    return render_template('jobs/created.html', email=email)


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

        send_admin_review_email(job)

        app.logger.info("Job ({}) was successfully edited.".format(job.id))

        session['edited_email'] = job.recruiter_email
        return redirect(url_for('edited'))

    locations = get_location_context()
    tags = get_tag_context()

    return render_template('jobs/create_or_edit.html',
                           form=form,
                           token=token,
                           locations=locations,
                           tags=tags,
                           prompt=CREATE_OR_UPDATE_PROMPT)


@app.route('/edited')
def edited():
    email = session.pop('edited_email', None)
    if not email:
        abort(404)
    return render_template('jobs/edited.html')


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
        return render_template('jobs/show_chromeless.html',
                               chromeless=True,
                               job=job)

    return render_template('jobs/preview_failed.html')


@app.route('/faq')
def how():
    return render_template('faq.html', prompt='Frequently asked questions.')
