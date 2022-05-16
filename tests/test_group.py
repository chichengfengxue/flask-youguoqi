from flask import url_for, session

from tests.test_auth import login
from ygq.models import Room, Notification, Message


def test_start_group(client):
    login(client)
    rv = client.post(url_for('user.start_group', username='user2'), follow_redirects=True)
    assert rv.status_code == 200
    assert b'user and user2 &#39;s group' in rv.data
    assert Room.query.get(1)
    assert Notification.query.get(2)

