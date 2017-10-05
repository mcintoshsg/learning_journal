'''
    All forms used by the app
'''
import datetime
import re

from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, TextAreaField, TextField, DateTimeField
from wtforms.validators import DataRequired, Email, Length


from models import User

def validate_url(form, field):
    ''' custom validator to ensure resources are URL's '''
    # url_regex = re.compile(r'''
    #     http[s]?://(?:[a-zA-Z]|
    #     [0-9]|[$-_@.&+]|[!*\(\),]
    #     |(?:%[0-9a-fA-F][0-9a-fA-F]))+''')
    
    url_regex = re.compile(r'(https?://\S+)')

    if not url_regex.search(field.data):
        field.errors.append("You must enter a URL in the fomat http(s)://...")

class LoginForm(FlaskForm):
    ''' the login form, further validations will take
        place on the HTML page
    '''
    email = StringField('Email',
                        validators=[DataRequired(),
                                    Email(message="That is not a valid email address!")])
    password = PasswordField('Password',
                             validators=[DataRequired(),
                                         Length(min=8, message='Passwords must be a minumum of 8 characters')])

class EntryForm(FlaskForm):
    ''' the entry form, shows all the journal entries '''
    title = StringField('Title', validators=[DataRequired(), Length(max=100)])
    entry_date = DateTimeField(default=datetime.datetime.now)
    duration = StringField('Time taken', validators=[DataRequired()])
    learnings = TextAreaField('What did you learn?', validators=[DataRequired()])
    resources = StringField("Enter URL for resource used", validators=[validate_url])
    tags = StringField('Enter a tag', validators=[DataRequired(), Length(max=30)])



  