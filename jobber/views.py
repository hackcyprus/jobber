"""
jobber.views
~~~~~~~~~~~~

View declarations.

"""
import logging
from random import choice

from flask import Blueprint
from flask import render_template, abort, redirect,  Response
from flask import url_for, session, request

from jobber import rss
from jobber.core.models import Job, EmailReviewToken
from jobber.core.forms import JobForm
from jobber.services import SearchService
from jobber.database import db
from jobber.conf import settings
from jobber.functions import send_instructory_email, send_confirmation_email
from jobber.view_helpers import (get_location_context,
                                 get_tag_context,
                                 populate_job,
                                 populate_form,
                                 send_review_email)


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


logger = logging.getLogger('jobber')


blueprint = Blueprint('views', __name__)


@blueprint.context_processor
def inject_swag():
    prompt = choice(PROMPTS)
    position = choice(EXAMPLE_POSITIONS)
    return dict(prompt=prompt, position=position)


@blueprint.route('/search/')
@blueprint.route('/')
def index():
    query = db.session.query(Job)\
              .filter_by(published=True)\
              .order_by(Job.created.desc())
    return render_template('index.html', jobs=query.all())


@blueprint.route('/search/<query>')
def search(query):
    service = SearchService()
    hits = service.search_jobs(query, sort=('created', 'desc'))
    return render_template('index.html', jobs=hits, query=query)


@blueprint.route('/create', methods=['GET', 'POST'])
def create():
    form = JobForm()

    if form.validate_on_submit():
        job = populate_job(form)

        # Create a token to enable email reviewing.
        review_token = EmailReviewToken(job=job)

        db.session.add(review_token)
        db.session.add(job)
        db.session.commit()

        send_instructory_email(job)
        send_review_email(job, review_token.token)

        logger.info("Job ({}) was successfully created.".format(job.id))

        session['created_email'] = job.recruiter_email
        return redirect(url_for('views.created'))

    locations = get_location_context()
    tags = get_tag_context()

    return render_template('jobs/create_or_edit.html',
                           form=form,
                           locations=locations,
                           tags=tags,
                           prompt=CREATE_OR_UPDATE_PROMPT)


@blueprint.route('/created')
def created():
    email = session.pop('created_email', None)
    if not email:
        abort(404)
    return render_template('jobs/created.html', email=email)


@blueprint.route('/edit/<int:job_id>/<token>', methods=['GET', 'POST'])
def edit(job_id, token):
    job = db.session.query(Job).filter_by(admin_token=token).first()

    if not (job and job_id == job.id):
        abort(404)

    form = populate_form(job)

    if form.validate_on_submit():
        job = populate_job(form, job=job)

        # An edited job is pending review so it needs to be unpublished.
        job.published = False

        # Create a token to enable email reviewing.
        review_token = EmailReviewToken(job=job)
        db.session.add(review_token)

        db.session.commit()

        send_review_email(job, review_token.token)

        logger.info("Job ({}) was successfully edited.".format(job.id))

        session['edited_email'] = job.recruiter_email
        return redirect(url_for('views.edited'))

    locations = get_location_context()
    tags = get_tag_context()

    return render_template('jobs/create_or_edit.html',
                           form=form,
                           token=token,
                           locations=locations,
                           tags=tags,
                           prompt=CREATE_OR_UPDATE_PROMPT)


@blueprint.route('/edited')
def edited():
    email = session.pop('edited_email', None)
    if not email:
        abort(404)
    return render_template('jobs/edited.html')


@blueprint.route('/jobs/<int:job_id>/<company_slug>/<job_slug>')
def show(job_id, company_slug, job_slug):
    job = db.session.query(Job).get(job_id)
    if not (job and job.published):
        abort(404)
    if job.slug == job_slug and job.company.slug == company_slug:
        return render_template('jobs/show.html', job=job)
    abort(404)


@blueprint.route('/preview', methods=['POST'])
def preview():
    form = JobForm()

    if form.validate_on_submit():
        job = populate_job(form)
        return render_template('jobs/show_chromeless.html',
                               chromeless=True,
                               job=job)

    return render_template('jobs/preview_failed.html', form=form)


@blueprint.route('/faq')
def how():
    return render_template('faq.html', prompt='Frequently asked questions.')


@blueprint.route('/feed/<query>')
@blueprint.route('/feed')
def feed(query=None):
    return Response(rss.render_feed(query=query), mimetype='text/xml')


@blueprint.route('/review/email/<token>', methods=['POST'])
def reviewed_via_email(token):
    """Returns a 200 if the review was successful, otherwise returns a 406 as
    per Mailgun's documentation:

    http://documentation.mailgun.com/user_manual.html#routes

    """
    sender = request.form['sender']
    reply = request.form['stripped-text'].strip()

    logger.info("Received email review request with token {} and reply '{}'."
                .format(token, reply))

    if sender not in settings.EMAIL_REVIEWERS:
        logger.info("Unauthorized email reviewer with email '{}' and token {}!"
                    .format(sender, token))
        abort(406)

    if reply != 'ok':
        logger.info("Bad reply, aborting review.")
        abort(406)

    token_model = db.session.query(EmailReviewToken).filter_by(token=token).first()
    if not token_model:
        logger.info("Unknown token {}, aborting review."
                    .format(token))
        abort(406)

    if token_model.used:
        logger.info("Token {} is already used, aborting review."
                    .format(token))
        abort(406)

    token_model.use()

    job = token_model.job

    was_published = False
    if not job.published:
        job.published = True
        was_published = True

    db.session.commit()

    # To avoid any race conditions between manually reviewing and reviewing via
    # email, we make a last check before sending the email.
    if was_published:
        send_confirmation_email(job)

    logger.info("Reviewed job ({}) via email with token {}."
                .format(job.id, token))

    return 'okay', 200
