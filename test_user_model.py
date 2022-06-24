"""User model tests."""

# run these tests like:
#
#    python -m unittest test_user_model.py


from app import app
import os
from unittest import TestCase

from models import db, User, Message, Follows

# BEFORE we import our app, let's set an environmental variable
# to use a different database for tests (we need to do this
# before we import our app, since that will have already
# connected to the database

os.environ['DATABASE_URL'] = "postgresql:///warbler_test"

# Now we can import app


# Create our tables (we do this here, so we only create the tables
# once for all tests --- in each test, we'll delete the data
# and create fresh new clean test data

db.create_all()


class UserModelTestCase(TestCase):
    def setUp(self):
        User.query.delete()

        u1 = User.signup("u1", "u1@email.com", "password", None)
        u2 = User.signup("u2", "u2@email.com", "password", None)

        db.session.commit()
        self.u1_id = u1.id
        self.u2_id = u2.id

        self.client = app.test_client()

    def tearDown(self):
        db.session.rollback()

    def test_user_model(self):
        """ Test if user model works """

        u1 = User.query.get(self.u1_id)

        # User should have no messages & no followers
        self.assertEqual(len(u1.messages), 0)
        self.assertEqual(len(u1.followers), 0)

    def test_user_repr(self):
        """ Test if repr method works """

        u1 = User.query.get(self.u1_id)

        self.assertEqual(
            u1.__repr__(), f'<User #{self.u1_id}: {u1.username}, {u1.email}>')

    def test_is_following(self):
        """ Test if user.is_following successfully detects a follow """

        u1 = User.query.get(self.u1_id)
        u2 = User.query.get(self.u2_id)

        u2.followers.append(u1)

        self.assertTrue(u1.is_following(u2))

    def test_is_not_following(self):
        """ Test if user.is_following returns false for non-follower """

        u1 = User.query.get(self.u1_id)
        u2 = User.query.get(self.u2_id)

        self.assertFalse(u1.is_following(u2))

    def test_is_followed_by(self):
        """ Test if user.is_followed_by returns true if followed by user """

        u1 = User.query.get(self.u1_id)
        u2 = User.query.get(self.u2_id)

        u1.following.append(u2)

        self.assertTrue(u2.is_followed_by(u1))

    def test_is_not_followed_by(self):
        """ Test if user.is_followed_by returns false if not followed by user """

        u1 = User.query.get(self.u1_id)
        u2 = User.query.get(self.u2_id)


        self.assertFalse(u2.is_followed_by(u1))

    def test_signup(self):
        """ Test if user can be signed up """

        u3 = User.signup("u3", "u3@email.com", "password", None)

        db.session.commit()

        signed_up_user = User.query.get(u3.id)

        self.assertEqual(u3, signed_up_user)

    def test_fail_signup(self):
        """ Test if user is not signed up if validations fail """

        error = False

        u3 = User.signup("u1", "BADEMAIL", "p", None)

        try:
            User.query.get(u3.id)
        except Exception:
            error = True

        self.assertTrue(error)


    def test_is_authenticated(self):
        """ Test if user's username and password is authentic """

        u1 = User.query.get(self.u1_id)

        auth = User.authenticate(u1.username, 'password')

        self.assertEqual(u1, auth)

    def test_username_not_authentic(self):
        """ Test if user's username is not authentic """

        u1 = User.query.get(self.u1_id)

        auth = User.authenticate('y1', 'password')

        self.assertNotEqual(u1, auth)

    def test_password_not_authentic(self):
        """ Test if user's password is not authentic """

        u1 = User.query.get(self.u1_id)

        auth = User.authenticate('u1', 'pas$sword')

        self.assertNotEqual(u1, auth)
