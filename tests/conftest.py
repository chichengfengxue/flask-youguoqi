import pytest

from ygq import create_app, db, User, Dish, Shop, File, Comment, Tag, Order, Rider


@pytest.fixture()
def client():
    app = create_app('testing')
    context = app.test_request_context()
    context.push()
    client = app.test_client()

    db.create_all()

    user = User(email='user@youguoqi.com', name='user', username='user', confirmed=True)
    unconfirmed_user = User(email='unconfirmed@youguoqi.com', name='unconfirmed',
                            username='unconfirmed', confirmed=False)
    user2 = User(email='user2@youguoqi.com', name='user2', username='user2', confirmed=True)
    user.set_password('123')
    unconfirmed_user.set_password('123')
    user2.set_password('123')
    rider1 = Rider(user_id=1)
    rider2 = Rider(user_id=2)
    rider3 = Rider(user_id=3)
    shop = Shop(
        name="FzuHotel",
        location_x=100,
        location_y=100,
        tel='12345678900',
        user=User.query.get(1)
    )
    file = File(filename="test.jpg", is_use=True, is_img=True)
    dish = Dish(
        name="FoTiaoQiang",
        description="佛跳墙又名福寿全，是福建省福州市的一道特色名菜，属闽菜系。",
        price=998,
        shop=shop,
        sales=0,
        prepare_time=60,
    )
    file.dish = dish
    comment = Comment(body='test comment body', dish=dish, author=user)
    tag = Tag(name='test tag')
    dish.tags.append(tag)
    order = Order(
        consumer_id=3,
        price=998,
        fare=15,
        number=1,
        dish_id=1,
        shop_id=1,
        is_finish=False,
        is_accept=False,
        is_prepared=False)
    db.session.add_all([user, user2, unconfirmed_user, dish, file, comment, tag, shop, order, rider1, rider2, rider3])
    db.session.commit()

    yield client

    db.drop_all()
    context.pop()


@pytest.fixture()
def runner():
    app = create_app('testing')
    context = app.test_request_context()
    context.push()
    runner = app.test_cli_runner()
    db.create_all()

    yield runner

    db.drop_all()
    context.pop()
