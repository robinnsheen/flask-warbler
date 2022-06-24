import os
from unittest import TestCase

from models import db, Message, User


os.environ['DATABASE_URL'] = "postgresql:///warbler_test"


from app import app, CURR_USER_KEY

app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False

db.create_all()

app.config['WTF_CSRF_ENABLED'] = False


class UserBaseViewTestCase(TestCase):
    def setUp(self):
        User.query.delete()

        u1 = User.signup("u1", "u1@email.com", "password", None)
        u2 = User.signup("u2", "u2@email.com", "password", None)

        db.session.flush()

        m1 = Message(text="m1-text", user_id=u1.id)
        m2 = Message(text="m2-text", user_id=u2.id)

        db.session.add_all([m1,m2])
        db.session.commit()

        self.u1_id = u1.id
        self.u2_id = u2.id

        self.m1_id = m1.id
        self.m2_id = m2.id

        self.client = app.test_client()


class UserAddViewTestCase(UserBaseViewTestCase):

    def test_add_message(self):
        # Since we need to change the session to mimic logging in,
        # we need to use the changing-session trick:
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.u1_id

            # Now, that session setting is saved, so we can have
            # the rest of ours test
            resp = c.post("/messages/new", data={"text": "Hello"})

            self.assertEqual(resp.status_code, 302)

            Message.query.filter_by(text="Hello").one()

    def test_show_followers(self):
        """ test if you can see followers page """
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.u1_id

            resp = c.get(f"users/{self.u1_id}/followers")

            html = resp.get_data(as_text=True)

            #TODO: grab a particular follower (element)
            self.assertEqual(resp.status_code, 200)
            self.assertIn("<!-- @followers (for Testing)-->",html)

    def test_show_following(self):
        """ test if user's followers appear on the following page"""
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.u1_id

            resp = c.get(f"users/{self.u1_id}/following")

            html = resp.get_data(as_text=True)


            self.assertEqual(resp.status_code, 200)
            self.assertIn("<!-- @following (for Testing)-->",html)

    def test_show_followers_diff_user(self):
        """ tests if other user can see another user's followers page """
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.u2_id

            resp = c.get(f"users/{self.u1_id}/followers")

            html = resp.get_data(as_text=True)


            self.assertEqual(resp.status_code, 200)
            self.assertIn("<!-- @followers (for Testing)-->",html)

    def test_show_following_diff_user(self):
        """ tests if you can see another user's following page"""
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.u2_id

            resp = c.get(f"users/{self.u1_id}/following")

            html = resp.get_data(as_text=True)


            self.assertEqual(resp.status_code, 200)
            self.assertIn("<!-- @following (for Testing)-->",html)



    def test_show_followers_id_logged_out(self):
        """ tests if you can't see followers if you are logged out"""
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = None

            resp = c.get(f"users/{self.u1_id}/followers",
            follow_redirects=True)

            html = resp.get_data(as_text=True)


            self.assertEqual(resp.status_code, 200)
            self.assertIn("<!-- @home-anon (for Testing)-->",html)

    def test_show_following_if_logged_out(self):
        """ tests that user can't see following if logged out"""
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = None

            resp = c.get(f"users/{self.u1_id}/following",
            follow_redirects=True)

            html = resp.get_data(as_text=True)


            self.assertEqual(resp.status_code, 200)
            self.assertIn("<!-- @home-anon (for Testing)-->",html)

