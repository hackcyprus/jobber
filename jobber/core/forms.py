from wtforms import TextField, SelectField, IntegerField
from wtforms.validators import DataRequired, Email, Optional, URL
from wtforms.widgets import HiddenInput, TextArea
from flask.ext.wtf import Form

from jobber.models import Job, Location


class JobForm(Form):
    """A `JobForm` is used for creating and updating posted jobs."""

    #: Job id (populated if used for updating).
    id = IntegerField('Id', widget=HiddenInput(), validators=[Optional()])

    #: Job title.
    title = TextField('Title', validators=[DataRequired()])

    #: Job description.
    description = TextField('Description',
                            widget=TextArea(),
                            validators=[DataRequired()])

    #: Job Type (full time, part time, contract or internship).
    job_type = SelectField('Job Type',
                           validators=[DataRequired()],
                           choices=Job.JOB_TYPES.items(),
                           coerce=int)

    #: Does the company accept remote workers?
    remote_work = SelectField('Remote Work?',
                              validators=[DataRequired()],
                              choices=Job.REMOTE_WORK_OPTIONS.items(),
                              coerce=int)

    #: Company id (populated if used for updating or auto-populated from a list
    #: of autocomplete suggestions).
    company__id = IntegerField('Company id',
                               widget=HiddenInput(),
                               validators=[Optional()])

    #: Company name (freetext).
    company__name = TextField('Company Name', validators=[DataRequired()])

    #: Company website (freetext).
    company__website = TextField('Company Website', validators=[Optional(), URL()])

    #: Location id (populated if used for updating).
    location__id = IntegerField('Location id',
                                widget=HiddenInput(),
                                validators=[Optional()])

    #: Location city (freetext).
    location__city = TextField('City', validators=[DataRequired()])

    #: Location country (country ISO code).
    location__country_code = SelectField('Country',
                                        validators=[DataRequired()],
                                        choices=Location.COUNTRIES.items())

    #: Contact method (email or url).
    contact_method = SelectField('Contact Method',
                                 validators=[DataRequired()],
                                 choices=Job.CONTACT_METHODS.items(),
                                 coerce=int)

    #: Contact email (if contact method is email).
    contact_email = TextField('Contact Email', validators=[Optional(), Email()])

    #: Contact url (if contact method is url).
    contact_url = TextField('Contact Link', validators=[Optional(), URL()])
