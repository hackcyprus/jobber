"""
jobber.models
~~~~~~~~~~~~~

Model declarations.

"""
from pprint import pformat
from extensions import db


class BaseModel(db.Model):
    __abstract__ = True

    def __repr__(self):
        name = self.__class__.__name__.capitalize()
        attrs = dict()
        for column in self.__table__.columns:
            attrs[column.name] = getattr(self, column.name)
        return "<{} {}>".format(name, pformat(attrs))


class Company(BaseModel):
    __tablename__ = 'companies'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(75), nullable=False)

    def __init__(self, name):
        self.name = name