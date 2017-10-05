'''
    Database models for the journal app
'''
import datetime

from flask_bcrypt import generate_password_hash
from flask_login import UserMixin
from peewee import *

DATABASE = SqliteDatabase('journal.db')


class User(UserMixin, Model):
    ''' The user model (table). UserMixin allows flask to deal with
        logins via the login manager
    '''
    email = CharField(unique=True)
    password = CharField(max_length=100)

    class Meta:
        ''' sort the database on the joined_at field '''
        database = DATABASE

    @classmethod
    def create_user(cls, email, password):
        ''' Create a user in our user table '''
        try:
            with DATABASE.transaction():
                cls.create(email=email,
                           password=generate_password_hash(password)
                          )
        except IntegrityError:
            raise ValueError('Email already exists')

    def get_entries(self):
        return Journal.select()

    def get_all_tagged_entries(self, tag):
        '''list all journals by a certain tag'''
        return Journal.select().where(
            (Journal.user == self) & Journal.tags.contains(tag))


class Journal(Model):
    ''' the journal model / table '''
    user = ForeignKeyField(rel_model=User, related_name='journals')
    title = CharField(unique=True, max_length=100)
    duration = CharField(max_length=100)
    learnings = TextField()
    resources = TextField()
    entry_date = DateTimeField(default=datetime.datetime.now)
    tags = CharField(max_length=100)

    class Meta:
        database = DATABASE
        order_by = ('-entry_date',)
    
def initalize():
    ''' setup the database '''
    DATABASE.connect()
    DATABASE.create_tables([User, Journal], safe=True)
    DATABASE.close()

