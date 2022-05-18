import os

import pytest
from flask import current_app
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import NoAlertPresentException
import unittest, time, re

from ygq import create_app, db, User, Dish, Shop, File, Comment, Tag, Order, Rider, socketio
from ygq.models import Message


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


@pytest.fixture(scope='session')
def driver():
    # os.environ['MOZ_HEADLESS'] = '1'
    driver = webdriver.Firefox()
    driver.implicitly_wait(5)  # 隐式等待

    yield driver

    # driver.quit()


@pytest.fixture(scope='session')
def driver2():
    # os.environ['MOZ_HEADLESS'] = '1'
    driver2 = webdriver.Firefox()
    driver2.implicitly_wait(5)  # 隐式等待

    yield driver2

    # driver2.quit()


@pytest.fixture(scope='function')
def driver_fn():
    # os.environ['MOZ_HEADLESS'] = '1'
    driver_fn = webdriver.Firefox()
    driver_fn.implicitly_wait(5)  # 隐式等待

    yield driver_fn

    # driver.quit()


