# -*- coding: utf-8 -*-
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import NoAlertPresentException
import unittest, time, re

from ygq import User


def test_ui_login_user(driver, email="ksun@ligang.net", username='leigong'):
    driver.get("http://127.0.0.1:5000/")
    try:
        driver.find_element_by_link_text("Login").click()
    except NoSuchElementException as e:  # 已登录
        test_ui_logout_user(driver)
        driver.get("http://127.0.0.1:5000/")
        driver.find_element_by_link_text("Login").click()
    finally:
        driver.find_element_by_id("email").click()
        driver.find_element_by_id("email").clear()
        driver.find_element_by_id("email").send_keys(email)
        driver.find_element_by_id("password").click()
        driver.find_element_by_id("password").clear()
        driver.find_element_by_id("password").send_keys("123456")
        driver.find_element_by_id("remember_me").click()
        driver.find_element_by_id("submit").click()
        assert username in driver.page_source


def test_ui_logout_user(driver):
    driver.get("http://127.0.0.1:5000/")
    try:
        driver.find_element_by_xpath("//div[@id='navbarColor01']/div[2]/div/a/img").click()
        driver.find_element_by_link_text("Logout").click()
    except NoSuchElementException as e:  # 未登录
        driver.get("http://127.0.0.1:5000/")
    finally:
        assert 'Join YouGuoQi' in driver.page_source


def test_ui_user_index(driver, email="ksun@ligang.net", username='leigong'):
    driver.get("http://127.0.0.1:5000/")
    try:
        driver.find_element_by_xpath("//div[@id='navbarColor01']/div[2]/div/a/img").click()
        driver.find_element_by_link_text("My Home").click()
    except NoSuchElementException as e:  # 未登录
        test_ui_login_user(driver, email, username)
        driver.find_element_by_xpath("//div[@id='navbarColor01']/div[2]/div/a/img").click()
        driver.find_element_by_link_text("My Home").click()
    finally:
        assert username+' \'s home' in driver.page_source


def test_ui_user_followers(driver, email="ksun@ligang.net", username='leigong'):
    test_ui_user_index(driver, email, username)
    driver.find_element_by_xpath("//a[contains(@href, '/user/leigong/followers')]").click()


def test_ui_access_follower(driver, followername=u'杨斌'):
    driver.find_element_by_link_text(followername).click()
    driver.find_element_by_xpath(u"//*/text()[normalize-space(.)='跟他聊天']/parent::*").click()


def test_ui_group_chat(driver, driver2):
    email = 'ksun@ligang.net'
    email2 = 'akang@yahoo.com'
    username = 'leigong'
    username2 = 'liujun'
    followername = u'杨斌'
    test_ui_login_user(driver, email="ksun@ligang.net", username='leigong')
    test_ui_user_index(driver, email="ksun@ligang.net", username='leigong')
    driver.find_element_by_xpath("//*/text()[normalize-space(.)='Follower']/parent::*").click()  # 查看用户关注者
    driver.find_element_by_link_text(followername).click()  # 访问关注者主页
    driver.find_element_by_xpath(u"//*/text()[normalize-space(.)='跟他聊天']/parent::*").click()  # 与用户2开始聊天
    time.sleep(5)
    assert username + ' 进入房间' in driver.page_source
    assert username+' and '+username2+' \'s group' in driver.page_source

    driver.find_element_by_id("message-textarea").click()
    driver.find_element_by_id("message-textarea").clear()
    driver.find_element_by_id("message-textarea").send_keys("hello")  # 用户1发送消息
    driver.find_element_by_id("group-meg-submit").click()
    assert 'hello' in driver.page_source

    test_ui_login_user(driver2, email="akang@yahoo.com", username='liujun')  # 用户2打开另一个客户端，并登录
    driver2.find_element_by_xpath("//div[@id='navbarColor01']/div[2]/a/span").click()  # 打开通知页面
    driver2.find_element_by_link_text(username+' and '+username2+' \'s group').click()
    assert username2 + ' 进入房间' in driver2.page_source
    assert 'hello' in driver2.page_source

    driver2.find_element_by_id("message-textarea").click()
    driver2.find_element_by_id("message-textarea").clear()
    driver2.find_element_by_id("message-textarea").send_keys("world")  # 用户2发送消息
    driver2.find_element_by_id("group-meg-submit").click()
    assert 'world' in driver2.page_source
    assert 'world' in driver.page_source















# def test_ui_login(driver_fn, email="ksun@ligang.net", username='leigong'):
#     # driver_fn = webdriver.Firefox()
#     driver_fn.get("http://127.0.0.1:5000/")
#     driver_fn.find_element_by_link_text("Login").click()
#     driver_fn.find_element_by_id("email").click()
#     driver_fn.find_element_by_id("email").clear()
#     driver_fn.find_element_by_id("email").send_keys(email)
#     driver_fn.find_element_by_id("password").click()
#     driver_fn.find_element_by_id("password").clear()
#     driver_fn.find_element_by_id("password").send_keys("123456")
#     driver_fn.find_element_by_id("remember_me").click()
#     driver_fn.find_element_by_id("submit").click()
