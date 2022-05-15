from flask import url_for

from ygq import User
from ygq.settings import Operations
from ygq.utils import generate_token


def login(client, email=None, password=None):
    if email is None and password is None:
        email = 'user@youguoqi.com'
        password = '123'

    return client.post(url_for('auth.login'), data=dict(
        email=email,
        password=password
    ), follow_redirects=True)


def logout(client):
    return client.get(url_for('auth.logout'), follow_redirects=True)


def test_login_user(client):
    rv = login(client)
    assert b'Login success.' in rv.data


def test_fail_login(client):
    rv = login(client, email='wrong-user@helloflask.com', password='wrong-password')
    assert b'Invalid email or password.' in rv.data


def test_logout_user(client):
    login(client)
    rv = logout(client)
    assert b'Logout success.' in rv.data


def test_unconfirmed_user_permission(client):
    login(client, email='unconfirmed@youguoqi.com', password='123')
    rv = client.get(url_for('chat.home'), follow_redirects=True)
    assert b'Please confirm your account first.' in rv.data


def test_register_account(client):
    rv = client.post(url_for('auth.register'), data=dict(
        name='register',
        email='register@helloflask.com',
        username='register',
        password='12345678',
        password2='12345678',
        location_x='1',
        location_y='1',
        tel='12345678900',
    ), follow_redirects=True)
    assert b'Confirm email sent, check your inbox.' in rv.data


def test_bad_confirm_token(client):
    login(client, email='unconfirmed@youguoqi.com', password='123')
    rv = client.get(url_for('auth.confirm', token='bad token'), follow_redirects=True)
    assert b'Invalid or expired token.' in rv.data
    assert b'Account confirmed.' not in rv.data


def test_confirm_account(client):
    user = User.query.filter_by(email='unconfirmed@youguoqi.com').first()
    assert not user.confirmed
    token = generate_token(user=user, operation='confirm')
    login(client, email='unconfirmed@youguoqi.com', password='123')
    rv = client.get(url_for('auth.confirm', token=token), follow_redirects=True)
    assert b'Account confirmed.' in rv.data
    assert user.confirmed


def test_reset_password(client):
    rv = client.post(url_for('auth.forget_password'), data=dict(
        email='user@youguoqi.com',
    ), follow_redirects=True)
    assert b'Password reset email sent, check your inbox.' in rv.data
    user = User.query.filter_by(email='user@youguoqi.com').first()
    assert user.validate_password('123')

    # bad token
    rv = client.post(url_for('auth.reset_password', token='bad token'), data=dict(
        email='user@youguoqi.com',
        password='new-password',
        password2='new-password'
    ), follow_redirects=True)
    assert b'Invalid or expired link.' in rv.data
    assert b'Password updated.' not in rv.data

    token = generate_token(user=user, operation=Operations.RESET_PASSWORD)
    rv = client.post(url_for('auth.reset_password', token=token), data=dict(
        email='user@youguoqi.com',
        password='new-password',
        password2='new-password'
    ), follow_redirects=True)
    assert b'Password updated.' in rv.data
    assert user.validate_password('new-password')
    assert not user.validate_password('123')



