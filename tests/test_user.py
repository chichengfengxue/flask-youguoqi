import io

from flask import url_for

from tests.test_auth import login, logout
from ygq import User, Dish
from ygq.settings import Operations
from ygq.utils import generate_token


def test_index_page(client):
    rv = client.get(url_for('user.index', username='unconfirmed'))
    assert b'unconfirmed' in rv.data


def test_show_collections(client):
    rv = client.get(url_for('user.show_collections', username='user'))
    assert b'No collection.' in rv.data

    user = User.query.get(1)
    user.collect(Dish.query.get(1))
    rv = client.get(url_for('user.show_collections', username='user'))
    assert b'No collection.' not in rv.data


def test_follow(client):
    rv = client.post(url_for('user.follow', username='user'), follow_redirects=True)
    assert b'Please log in to access this page.' in rv.data

    login(client, email='unconfirmed@youguoqi.com', password='123')
    rv = client.post(url_for('user.follow', username='user'), follow_redirects=True)
    assert b'Please confirm your account first.' in rv.data

    logout(client)
    login(client)
    rv = client.post(url_for('user.follow', username='unconfirmed'), follow_redirects=True)
    assert rv.status_code == 200
    assert b'User followed.' in rv.data

    rv = client.post(url_for('user.follow', username='unconfirmed'), follow_redirects=True)
    assert rv.status_code == 200
    assert b'Already followed.' in rv.data


def test_unfollow(client):
    rv = client.post(url_for('user.follow', username='user'), follow_redirects=True)
    assert b'Please log in to access this page.' in rv.data

    login(client)
    rv = client.post(url_for('user.unfollow', username='unconfirmed'), follow_redirects=True)
    assert rv.status_code == 200
    assert b'Not follow yet.' in rv.data

    client.post(url_for('user.follow', username='unconfirmed'), follow_redirects=True)

    rv = client.post(url_for('user.unfollow', username='unconfirmed'), follow_redirects=True)
    assert rv.status_code == 200
    assert b'User unfollowed.' in rv.data


def test_show_followers(client):
    user = User.query.get(1)
    user.follow(User.query.get(2))

    rv = client.get(url_for('user.show_followers', username='user'))
    assert b'unconfirmed' in rv.data
    assert b'user\'s following' in rv.data


def test_edit_profile(client):
    login(client)
    rv = client.post(url_for('user.edit_profile'), data=dict(
        username='newname',
        name='New Name',
        location_x='100',
        location_y='100',
        tel='12345678900'
    ), follow_redirects=True)
    assert b'Profile updated.' in rv.data
    user = User.query.get(1)
    assert user.name == 'New Name'
    assert user.username == 'newname'


def test_change_avatar(client):
    login(client)
    rv = client.get(url_for('user.change_avatar'))
    assert rv.status_code == 200
    assert b'Change Avatar' in rv.data


def test_upload_avatar(client):
    login(client)
    data = {'image': (io.BytesIO(b"abcdef"), 'test.jpg')}
    rv = client.post(url_for('user.upload_avatar'), data=data, follow_redirects=True,
                     content_type='multipart/form-data')
    assert b'Image uploaded, please crop.' in rv.data


def test_change_password(client):
    user = User.query.get(1)
    assert user.validate_password('123')

    login(client)
    rv = client.post(url_for('user.change_password'), data=dict(
        old_password='123',
        password='new-password',
        password2='new-password',
    ), follow_redirects=True)
    assert b'Password updated.' in rv.data
    assert user.validate_password('new-password')
    assert not user.validate_password('123')


def test_change_email(client):
    user = User.query.get(1)
    assert user.email == 'user@youguoqi.com'
    token = generate_token(user=user, operation=Operations.CHANGE_EMAIL, new_email='new@youguoqi.com')

    login(client)
    rv = client.get(url_for('user.change_email', token=token), follow_redirects=True)
    assert b'Email updated.' in rv.data
    assert user.email == 'new@youguoqi.com'

    rv = client.get(url_for('user.change_email', token='bad'), follow_redirects=True)
    assert b'Invalid or expired token.' in rv.data


def test_delete_account(client):
    login(client)
    rv = client.post(url_for('user.delete_account'), data=dict(
        username='user',
    ), follow_redirects=True)
    assert b'Your are free, goodbye!' in rv.data
    assert User.query.filter_by(username='user').first() is None
