"""
jobber.views
~~~~~~~~~~~~

View declarations.

"""
from random import choice
from flask import render_template, abort, redirect

from jobber.app import app
from jobber.models import Job, Location, Company
from jobber.core.search import Index
from jobber.core.forms import NewPositionForm
from jobber.extensions import db


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


def create_position(form):
    """Creates a new job position from a form submission.

    :param form: A `NewPositionForm` instance.

    """
    form_data = form.data
    company_id = form_data.get('company_id')
    company = None

    print form_data

    if company_id:
        company_id = int(company_id)
        company = Company.query.get(company_id)

    if not company:
        name = form_data['company_name']
        website = form_data.get('company_website')
        company = Company(name=name)
        if website:
            company.website = website
        db.session.add(company)

    city = form_data['city']
    country_code = form_data['country_code']
    location = Location(city=city, country_code=country_code)
    db.session.add(location)

    title = form_data['title']
    description = form_data['description']
    job_type = form_data['job_type']
    contact_method = form_data['contact_method']
    remote_work = form_data['remote_work']

    position = Job(title=title,
                   description=description,
                   job_type=job_type,
                   remote_work=remote_work,
                   contact_method=contact_method,
                   location=location,
                   company=company)

    if Job.human_contact_method == 'Link':
        position.contact_url = form_data['contact_url']
    else:
        position.contact_email = form_data['contact_email']

    db.session.add(position)
    db.session.commit()

    return position


@app.route('/search/')
@app.route('/')
def index():
    jobs = Job.query.filter_by(published=False)
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


@app.route('/new', methods=['GET', 'POST'])
def new():
    form = NewPositionForm()
    if form.validate_on_submit():
        create_position(form)
        return redirect('/')
    return render_template('create_job.html',
                           prompt='Great jobs, great people.',
                           form=form)


@app.route('/how')
def how():
    return 'how it works'


@app.route('/jobs/<int:job_id>/<company_slug>/<job_slug>')
def view(job_id, company_slug, job_slug):
    job = Job.query.get_or_404(job_id)
    if job.slug == job_slug and job.company.slug == company_slug:
        return render_template('job.html', job=job)
    abort(404)
