from wtforms import TextField, BooleanField, SelectField, HiddenField
from wtforms.validators import DataRequired
from flask.ext.wtf import Form

from jobber.models import Job, Location


required = DataRequired()


class NewPositionForm(Form):
    #: Job title.
    title = TextField('Title', validators=[required])

    #: Job description.
    description = TextField('Description', validators=[required])

    #: Job Type (full time, part time, contract or internship).
    job_type = SelectField('Job Type',
                           validators=[required],
                           choices=Job.JOB_TYPES.items(),
                           coerce=int)

    #: Does the company accept remote workers?
    remote_work = BooleanField('Remote Work?')

    #: Company Id. Auto-populated from the list of autocomplete suggestions.
    company_id = HiddenField('Company id')

    #: Company name (freetext).
    company_name = TextField('Company Name', validators=[required])

    #: Company website (freetext).
    company_website = TextField('Company Website')

    #: Location city (freetext).
    city = TextField('City', validators=[required])

    #: Location country (country ISO code).
    country_code = SelectField('Country',
                               validators=[required],
                               choices=Location.COUNTRIES.items())

    #: Contact method (email or url).
    contact_method = SelectField('Contact Method',
                                 validators=[required],
                                 choices=Job.CONTACT_METHODS.items(),
                                 coerce=int)

    #: Contact email (if contact method is email).
    contact_email = TextField('Contact Email')

    #: Contact url (if contact method is url).
    contact_url = TextField('Contact Link')
