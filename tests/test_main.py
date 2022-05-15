from flask import url_for, current_app

from tests.test_auth import login
from ygq import User, Notification, db, File, Dish, Shop


def test_app_exist(client):
    assert current_app


def test_app_is_testing(client):
    assert current_app.config['TESTING']


def test_404_error(client):
    rv = client.get('/foo')
    assert rv.status_code == 404
    assert b'Page Not Found' in rv.data


def test_index_page(client):
    rv = client.get('/')
    assert b'Join YouGuoQi' in rv.data

    login(client)
    rv = client.get(url_for('main.index'))
    assert b'My Home' in rv.data
    assert b'Join YouGuoQi' not in rv.data


def test_explore_page(client):
    rv = client.get(url_for('main.explore'))
    assert b'Change' in rv.data


def test_search(client):
    rv = client.get(url_for('main.search', q=''), follow_redirects=True)
    assert b'Enter keyword about dish, user or tag.' in rv.data

    rv = client.get(url_for('main.search', q='unconfirmed'))
    assert b'Enter keyword about dish, user or tag.' not in rv.data
    assert b'No results.' in rv.data

    rv = client.get(url_for('main.search', q='unconfirmed', category='tag'))
    assert b'Enter keyword about dish, user or tag.' not in rv.data
    assert b'No results.' in rv.data

    rv = client.get(url_for('main.search', q='unconfirmed', category='user'))
    assert b'Enter keyword about dish, user or tag.' not in rv.data
    assert b'No results.' not in rv.data
    assert b'unconfirmed' in rv.data


def test_show_notifications(client):
    user = User.query.get(1)
    notification = Notification(message='test', receiver=user)
    db.session.add(notification)
    db.session.commit()

    login(client)
    rv = client.get(url_for('main.show_notifications'))
    assert b'test' in rv.data


def test_show_dish(client):
    rv = client.get(url_for('main.show_dish', dish_id=1), follow_redirects=True)
    assert b'test tag' in rv.data
    assert b'test comment body' in rv.data
    assert b'Buy' not in rv.data
    assert b'Delete' not in rv.data

    login(client, email='unconfirmed@youguoqi.com', password="123")
    rv = client.get(url_for('main.show_dish', dish_id=1), follow_redirects=True)
    assert b'Buy' in rv.data

    login(client)
    rv = client.get(url_for('main.show_dish', dish_id=1), follow_redirects=True)
    assert b'Delete' in rv.data


def test_collect(client):
    assert Dish.query.get(1).collectors == []

    login(client)
    rv = client.post(url_for('main.collect', dish_id=1), follow_redirects=True)
    assert b'Dish collected.' in rv.data
    assert Dish.query.get(1).collectors[0].collector.name == 'user'

    rv = client.post(url_for('main.collect', dish_id=1), follow_redirects=True)
    assert b'Already collected.' in rv.data


def test_uncollect(client):
    login(client)
    client.post(url_for('main.collect', dish_id=1), follow_redirects=True)

    rv = client.post(url_for('main.uncollect', dish_id=1), follow_redirects=True)
    assert b'Dish uncollected.' in rv.data

    rv = client.post(url_for('main.uncollect', dish_id=1), follow_redirects=True)
    assert b'Not collect yet.' in rv.data


def test_new_comment(client):
    login(client)
    rv = client.post(url_for('main.new_comment', dish_id=1), data=dict(
        body='test comment from user.'
    ), follow_redirects=True)
    assert b'Comment published.' in rv.data
    assert Dish.query.get(1).comments[1].body == 'test comment from user.'


def test_reply_comment(client):
    login(client)
    rv = client.get(url_for('main.reply_comment', comment_id=1), follow_redirects=True)
    assert b'Reply to' in rv.data


def test_show_tag(client):
    rv = client.get(url_for('main.show_tag', tag_id=1))
    assert b'Order by time' in rv.data

    rv = client.get(url_for('main.show_tag', tag_id=1, order='by_collects'))
    assert b'Order by collects' in rv.data




