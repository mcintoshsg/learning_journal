import unittest

from playhouse.test_utils import test_database
from peewee import *

import journal
from models import User, Journal

TEST_DB = SqliteDatabase(':memory:')
TEST_DB.connect()
TEST_DB.create_tables([User, Journal,], safe=True)

USER_DATA = {
    'email': 'test_0@example.com',
    'password': 'password'
}

class UserModelTestCase(unittest.TestCase):
    ''' test cases for the user model '''
    @staticmethod # static method as it does not access anything in the class
    def create_users(count=2):
        ''' this test creates 2 users in the database via a function called
            create_users - which is is a class method
        '''

        for i in range(count):
            User.create_user(
                email='test_{}@example.com'.format(i),
                password='password'
            )

    def test_create_user(self):
        ''' test the creation of the user '''
        with test_database(TEST_DB, (User,)):
            self.create_users()
            self.assertEqual(User.select().count(), 2)
            self.assertNotEqual(
                User.select().get().password,
                'password'
            )

    def test_create_duplicate_user(self):
        ''' test to make each user is unique '''
        with test_database(TEST_DB, (User,)):
            self.create_users()
            with self.assertRaises(ValueError):
                User.create_user(
                    email='test_1@example.com',
                    password='password'
                )

'''
class UserViewsTestCase(ViewTestCase):

    def test_good_login(self):
        with test_database(TEST_DB, (User,)):
            UserModelTestCase.create_users(1)
            rv = self.app.post('/login', data=USER_DATA)
            self.assertEqual(rv.status_code, 302)
            self.assertEqual(rv.location, 'http://localhost/')

    def test_bad_login(self):
        with test_database(TEST_DB, (User,)):
            rv = self.app.post('/login', data=USER_DATA)
            self.assertEqual(rv.status_code, 200)

    def test_logout(self):
        with test_database(TEST_DB, (User,)):
            # Create and login the user
            UserModelTestCase.create_users(1)
            self.app.post('/login', data=USER_DATA)

            rv = self.app.get('/logout')
            self.assertEqual(rv.status_code, 302)
            self.assertEqual(rv.location, 'http://localhost/')

'''

if __name__ == '__main__':
    unittest.main()
