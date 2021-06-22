from playhouse.flask_utils import FlaskDB
from peewee import CharField


db = FlaskDB()


class Polynomial(db.Model):

    expression = CharField(unique=True)
