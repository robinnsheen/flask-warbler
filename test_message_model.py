"""User model tests."""


from app import app
import os
from unittest import TestCase

from models import db, User, Message, Follows

os.environ['DATABASE_URL'] = "postgresql:///warbler_test"

db.create_all()


class MessageModelTestCase(TestCase):
    def setUp(self):
        # deleting a user will delete all messages (b/c of cascade)
        User.query.delete()

        u1 = User.signup("u1", "u1@email.com", "password", None)
        db.session.flush()

        msg = Message(text='warble',user_id=u1.id)

        db.session.add(msg)

        db.session.commit()

        self.u1_id = u1.id
        self.m1_id = msg.id

        self.client = app.test_client()

    def tearDown(self):
        db.session.rollback()

    def test_message_model(self):
        """ Test if message model works """

        m1 = Message.query.get(self.m1_id)

        self.assertEqual(len(m1.user.messages), 1)
        self.assertEqual(len(m1.users_favorited), 0)
