from flask_wtf import FlaskForm
from wtforms import (
    StringField,
    SubmitField,
    TextAreaField
)
from wtforms.validators import DataRequired


class SearchForm(FlaskForm):
    search_bar = StringField("Search", validators=[DataRequired()])
    submit = SubmitField("Submit")

class SymptomsForm(FlaskForm):
    symptoms = TextAreaField("Symptoms", validators=[DataRequired()])
    submit = SubmitField("Submit")