from flask import url_for

from tests.test_auth import login, logout
from ygq import Order, Notification, User, db, Rider


def test_index_page(client):
    rv = client.get(url_for('rider.index', rider_id=1))
    assert rv.status_code == 200
    assert b'user\'rider' in rv.data


def test_finish_order(client):
    order = Order.query.get(1)
    order.is_accept = True
    order.rider = Rider.query.get(2)
    user = User.query.get(2)
    user.confirmed = True
    db.session.commit()

    login(client)
    rv = client.post(url_for('rider.finish_order', order_id=1), follow_redirects=True)
    assert rv.status_code == 403
    assert b'Forbidden' in rv.data

    logout(client)
    login(client, email='unconfirmed@youguoqi.com', password="123")

    rv = client.post(url_for('rider.finish_order', order_id=1), follow_redirects=True)
    print(rv.data)
    assert rv.status_code == 200
    assert Order.query.get(1).is_finish
    assert Rider.query.get(2).income == 15
    assert Notification.query.get(1)
