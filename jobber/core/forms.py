from wtforms import Field, TextField, SelectField, IntegerField
from wtforms.validators import DataRequired, Email, Optional, Length
from wtforms.widgets import HiddenInput, TextArea, TextInput
from flask.ext.wtf import Form

from jobber.core.models import Job, Location
from jobber.core.utils import parse_tags, clean_html


class TagListField(Field):
    widget = TextInput()

    def _value(self):
        tags = []

        if not self.data:
            return u''

        for tag in self.data:
            if hasattr(tag, 'slug'):
                tag = tag.slug
            tags.append(tag)

        return u','.join(tags)

    def process_formdata(self, valuelist):
        if valuelist:
            valuelist = valuelist[0]
        self.data = parse_tags(valuelist)


class JobForm(Form):
    """A `JobForm` is used for creating and updating posted jobs."""

    #: Job id (populated if used for updating).
    id = IntegerField('Id', widget=HiddenInput(), validators=[Optional()])

    #: Job title.
    title = TextField('Title', validators=[DataRequired(), Length(max=100)])

    #: Job description.
    description = TextField('Description',
                            widget=TextArea(),
                            validators=[DataRequired()],
                            filters=[clean_html])

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

    #: Company id (populated if used for updating).
    company__id = IntegerField('Company id',
                                widget=HiddenInput(),
                                validators=[Optional()])

    #: Company name (freetext).
    company__name = TextField('Company Name',
                               validators=[DataRequired(), Length(max=75)])

    #: Company website (freetext).
    company__website = TextField('Company Website',
                                 validators=[Optional(), Length(max=200)])

    #: Location id (populated if used for updating).
    location__id = IntegerField('Location id',
                                widget=HiddenInput(),
                                validators=[Optional()])

    #: Location city (freetext).
    location__city = TextField('City',
                               validators=[DataRequired(), Length(max=75)])

    #: Location country (country ISO code).
    location__country_code = SelectField('Country',
                                         validators=[DataRequired(), Length(max=3)],
                                         choices=Location.COUNTRIES.items())

    #: Contact method (email or url).
    contact_method = SelectField('Contact Method',
                                 validators=[DataRequired()],
                                 choices=Job.CONTACT_METHODS.items(),
                                 coerce=int)

    #: Contact email (if contact method is email).
    contact_email = TextField('Contact Email',
                              validators=[Optional(), Email(), Length(max=150)])

    #: Contact url (if contact method is url).
    contact_url = TextField('Contact Link',
                             validators=[Optional(), Length(max=200)])

    #: Recruiter name (freetext).
    recruiter_name = TextField('Recruiter Name',
                                validators=[DataRequired(), Length(max=100)])

    #: Recruiter email (email obviously).
    recruiter_email = TextField('Recruiter Email',
                                 validators=[Email(), Length(max=150)])

    #: Job tags.
    tags = TagListField('Tags', validators=[Optional()])
