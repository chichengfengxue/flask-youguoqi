# -*- coding: utf-8 -*-
import re
import time

import pytest
from selenium.common.exceptions import NoSuchElementException

from tests.utils import ui_login_user, ui_start_chat, ui_sent_message, ui_enter_group, ui_buy, ui_register_user
from ygq.fakes import fake


def test_001_ui_login(driver_fn):
    """登录成功"""
    email = "ksun@ligang.net"
    username = 'leigong'
    password = '123456'
    ui_login_user(driver_fn, email, username, password)
    assert username in driver_fn.page_source


def test_002_ui_login(driver_fn):
    """已登录用户无法再登录"""
    email = "ksun@ligang.net"
    username = 'leigong'
    password = '123456'
    ui_login_user(driver_fn, email, username, password)

    with pytest.raises(NoSuchElementException):
        ui_login_user(driver_fn, email, username, password)


def test_003_ui_login(driver_fn):
    """密码错误"""
    email = "ksun@ligang.net"
    username = 'leigong'
    password = '123456789'
    ui_login_user(driver_fn, email, username, password)
    assert 'Invalid email or password.' in driver_fn.page_source


def test_004_ui_group_chat(driver, driver2):
    email = 'ksun@ligang.net'
    email2 = 'akang@yahoo.com'
    username = 'leigong'
    username2 = 'liujun'
    room_name = username + ' and ' + username2 + ' \'s group'

    # 发起聊天，进入房间
    ui_login_user(driver, email, username)
    ui_start_chat(driver, username2)
    assert username + ' 进入房间' in driver.page_source
    assert username + ' and ' + username2 + ' \'s group - YouGuoQi' == driver.title

    # 用户1发送消息
    ui_sent_message(driver, message='Hello')
    assert 'Hello' in driver.page_source

    # 用户2进入群聊
    ui_login_user(driver2, email2, username2)
    ui_enter_group(driver2, room_name)
    assert username2 + ' 进入房间' in driver2.page_source
    assert 'Hello' in driver2.page_source

    # 用户2发送消息
    ui_sent_message(driver2, message='World')
    assert 'World' in driver2.page_source
    assert 'World' in driver.page_source


def test_005_ui_buy(driver_fn):
    email = 'ksun@ligang.net'
    username = 'leigong'
    dish_id = 1
    number = 1
    fare = 1

    ui_login_user(driver_fn, email, username)
    ui_buy(driver_fn, dish_id, number, fare)
    assert 'Successfully ordered!' in driver_fn.page_source
    assert '/user/order/' in driver_fn.current_url
    assert u'数量 '+str(number) in driver_fn.page_source
    assert u'运费 ' + str(fare) in driver_fn.page_source


def test_006_ui_delivery(driver_fn):
    email = 'ksun@ligang.net'
    username = 'leigong'

    ui_login_user(driver_fn, email, username)
    driver_fn.get("http://127.0.0.1:5000/delivery/")
    driver_fn.accept_next_alert = True
    driver_fn.find_element_by_xpath("//div[26]/div[2]/div[4]/button").click()
    alert = driver_fn.switch_to.alert
    assert alert.text == r"您确定要接单吗?"
    alert.accept()


def test_007_ui_register_user(driver_fn):
    """已登录用户注册"""
    email = 'ksun@ligang.net'
    username = 'leigong'
    tel = fake.phone_number()
    password = "youguoqi123"
    password2 = "youguoqi123"
    location_x = '10'
    location_y = '10'
    data = {'email': email, 'username': username, 'tel': tel, 'password': password,
            'password2': password2, 'location_x': location_x, 'location_y': location_y}
    ui_login_user(driver_fn, email, username)

    with pytest.raises(NoSuchElementException):
        ui_register_user(driver_fn, data)


def test_008_ui_register_user(driver_fn):
    """正常用户注册"""
    email = fake.email()
    username = fake.user_name()
    tel = fake.phone_number()
    password = "youguoqi123"
    password2 = "youguoqi123"
    location_x = '10'
    location_y = '10'
    data = {'email': email, 'username': username, 'tel': tel, 'password': password,
            'password2': password2, 'location_x': location_x, 'location_y': location_y}

    ui_register_user(driver_fn, data)
    assert 'Confirm email sent, check your inbox.' in driver_fn.page_source
    ui_login_user(driver_fn, email, username, password)
    assert username in driver_fn.page_source


def test_009_ui_register_user(driver_fn):
    """用户注册信息为空"""
    data = {'email': '', 'username': '', 'tel': '', 'password': '',
            'password2': '', 'location_x': '', 'location_y': ''}

    ui_register_user(driver_fn, data)
    # assert "请填写此栏" in driver_fn.page_source


def test_010_ui_register_user(driver_fn):
    """邮箱错误用户注册"""
    email = 'WrongEmail'
    username = fake.user_name()
    tel = fake.phone_number()
    password = "youguoqi123"
    password2 = "youguoqi123"
    location_x = '10'
    location_y = '10'
    data = {'email': email, 'username': username, 'tel': tel, 'password': password,
            'password2': password2, 'location_x': location_x, 'location_y': location_y}

    ui_register_user(driver_fn, data)
    assert "Invalid email address." in driver_fn.page_source


def test_011_ui_register_user(driver_fn):
    """电话号码错误用户注册"""
    email = fake.user_name()
    username = fake.user_name()
    tel = "d123"
    password = "youguoqi123"
    password2 = "youguoqi123"
    location_x = '10'
    location_y = '10'
    data = {'email': email, 'username': username, 'tel': tel, 'password': password,
            'password2': password2, 'location_x': location_x, 'location_y': location_y}

    ui_register_user(driver_fn, data)
    assert "Field must be between 6 and 20 characters long." in driver_fn.page_source