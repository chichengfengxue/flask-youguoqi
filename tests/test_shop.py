from flask import url_for

from tests.test_auth import login, logout
from ygq import Dish, User, db, Order


def test_index_page(client):
    rv = client.get(url_for('shop.index', shop_id=1))
    assert b'FzuHotel' in rv.data
    assert b'FoTiaoQiang' in rv.data


def test_show_orders(client):
    rv = client.get(url_for('shop.show_orders', shop_id=1))
    assert b'FoTiaoQiang' in rv.data
    assert b'998*1' in rv.data


def test_apply2shop(client):
    user = User.query.get(2)
    user.confirmed = True
    db.session.commit()
    login(client, email='unconfirmed@youguoqi.com', password="123")
    rv = client.post(url_for('shop.apply2shop', username='unconfirmed'), data=dict(
        name='ShaXianHotel',
        location_x='100',
        location_y='100',
        tel='98765432100'
    ), follow_redirects=True)
    assert rv.status_code == 200
    assert b'Shop published.' in rv.data


def test_delete_dish(client):
    login(client, email='unconfirmed@youguoqi.com', password="123")
    rv = client.post(url_for('shop.delete_dish', dish_id=1), follow_redirects=True)
    assert rv.status_code == 403
    assert b'Forbidden' in rv.data

    logout(client)
    login(client)
    rv = client.post(url_for('shop.delete_dish', dish_id=1), follow_redirects=True)
    assert rv.status_code == 200
    assert b'Dish deleted.' in rv.data
    assert Dish.query.get(1) is None


def test_new_dish(client):
    login(client, email='unconfirmed@youguoqi.com', password="123")
    rv = client.post(url_for('shop.new_dish', shop_id=1), data=dict(
        price=100,
        description='form.description.data',
        shop_id=1,
        prepare_time=20,
        name='form.name.data'
    ), follow_redirects=True)
    assert rv.status_code == 403
    assert b'Forbidden' in rv.data

    logout(client)
    login(client)
    rv = client.post(url_for('shop.new_dish', shop_id=1), data=dict(
        price=100,
        description='form.description.data',
        shop_id=1,
        prepare_time=20,
        name='test'
    ), follow_redirects=True)
    assert rv.status_code == 200
    assert b'Dish published.' in rv.data
    assert Dish.query.get(2).name == 'test'


def test_edit_description(client):
    assert Dish.query.get(1).description == '佛跳墙又名福寿全，是福建省福州市的一道特色名菜，属闽菜系。'

    login(client, email='unconfirmed@youguoqi.com', password="123")
    rv = client.post(url_for('shop.edit_description', dish_id=1), data=dict(
        description='test description.'
    ), follow_redirects=True)
    assert rv.status_code == 403
    assert b'Forbidden' in rv.data

    logout(client)
    login(client)

    rv = client.post(url_for('shop.edit_description', dish_id=1), data=dict(
        description='test description.'
    ), follow_redirects=True)
    assert b'Description updated.' in rv.data
    assert Dish.query.get(1).description == 'test description.'


def test_new_tag(client):
    assert Dish.query.get(1).tags[0].name == 'test tag'

    login(client, email='unconfirmed@youguoqi.com', password="123")
    rv = client.post(url_for('shop.new_tag', dish_id=1), data=dict(
        tag='test test hello world '
    ), follow_redirects=True)
    assert rv.status_code == 403
    assert b'Forbidden' in rv.data

    logout(client)
    login(client)

    rv = client.post(url_for('shop.new_tag', dish_id=1), data=dict(
        tag='test test hello world '
    ), follow_redirects=True)
    assert rv.status_code == 200
    assert b'Tag added.' in rv.data
    assert Dish.query.get(1).tags[1].name == 'test'
    assert Dish.query.get(1).tags[2].name == 'hello'
    assert Dish.query.get(1).tags[3].name == 'world'


def test_finish_order(client):
    login(client, email='unconfirmed@youguoqi.com', password="123")
    rv = client.post(url_for('shop.finish_order', order_id=1), follow_redirects=True)
    assert rv.status_code == 403
    assert b'Forbidden' in rv.data

    logout(client)
    login(client)
    client.post(url_for('shop.finish_order', order_id=1), follow_redirects=True)
    assert Order.query.get(1).is_prepared
