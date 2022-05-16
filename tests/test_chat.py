import flask_login
import pytest
from flask import current_app, url_for
from flask_login import current_user

from tests.test_auth import login, logout
from ygq import socketio, User, db
from ygq.models import Message
from ygq.wsgi import app


def test_new_message_event(client):
    @app.login_manager.request_loader
    def load_user_from_request(request):
        return User.query.get(1)

    socketio_client = socketio.test_client(current_app)
    socketio_client.get_received()
    socketio_client.emit('new message', 'Hello, Test')
    received = socketio_client.get_received()
    assert received[0]['name'] == 'new message'
    assert received[0]['args'][0]['message_body'] == '<p>Hello, Test</p>'
    assert Message.query.filter_by(author_id=1).count() == 1
    assert User.query.get(1).messages[0].body == '<p>Hello, Test</p>'

    rv = client.get(url_for('chat.home'))
    assert b'Hello, Test' in rv.data

    socketio_client.disconnect()

    @app.login_manager.request_loader
    def load_user_from_request(request):
        pass


def test_home_page(client):
    message1 = Message(body='Test Message 1', author_id=1)
    message2 = Message(body='Test Message 2', author_id=2)
    message3 = Message(body='Test Message 3', author_id=1)
    db.session.add_all([message1, message2, message3])
    db.session.commit()

    login(client)
    rv = client.get(url_for('chat.home'))
    assert b'Test Message 1' in rv.data
    assert b'Test Message 2' in rv.data
    assert b'Test Message 3' in rv.data


def test_get_messages(client):
    message1 = Message(body='Test Message 1', author_id=1)
    message2 = Message(body='Test Message 2', author_id=2)
    message3 = Message(body='Test Message 3', author_id=1)
    db.session.add_all([message1, message2, message3])
    db.session.commit()

    login(client)
    current_app.config['YGQ_MESSAGE_PER_PAGE'] = 1
    rv = client.get(url_for('chat.home'))
    assert b'Test Message 3' in rv.data
    assert b'Test Message 1' not in rv.data
    assert b'Test Message 2' not in rv.data

    rv = client.get(url_for('chat.get_messages', page=1))
    assert b'Test Message 3' in rv.data
    assert b'Test Message 1' not in rv.data
    assert b'Test Message 2' not in rv.data

    rv = client.get(url_for('chat.get_messages', page=2))
    assert b'Test Message 2' in rv.data
    assert b'Test Message 1' not in rv.data
    assert b'Test Message 3' not in rv.data

    rv = client.get(url_for('chat.get_messages', page=3))
    assert b'Test Message 1' in rv.data
    assert b'Test Message 2' not in rv.data
    assert b'Test Message 3' not in rv.data
