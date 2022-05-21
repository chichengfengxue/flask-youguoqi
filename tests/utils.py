import re
import time

from selenium.common.exceptions import NoSuchElementException

from ygq.fakes import fake


def ui_register_user(driver, data):
    email = data['email']
    username = data['username']
    tel = data['tel']
    password = data['password']
    password2 = data['password2']
    location_x = data['location_x']
    location_y = data['location_y']

    driver.get("http://127.0.0.1:5000/")
    driver.find_element_by_link_text("Join YouGuoQi").click()
    driver.find_element_by_link_text("Join YouGuoQi").click()
    driver.find_element_by_id("name").click()
    driver.find_element_by_id("name").clear()
    driver.find_element_by_id("name").send_keys(username)
    driver.find_element_by_id("email").click()
    driver.find_element_by_id("email").clear()
    driver.find_element_by_id("email").send_keys(email)
    driver.find_element_by_id("username").click()
    driver.find_element_by_id("username").clear()
    driver.find_element_by_id("username").send_keys(username)
    driver.find_element_by_id("location_x").click()
    driver.find_element_by_id("location_x").clear()
    driver.find_element_by_id("location_x").send_keys(location_x)
    driver.find_element_by_id("location_y").click()
    driver.find_element_by_id("location_y").clear()
    driver.find_element_by_id("location_y").send_keys(location_y)
    driver.find_element_by_id("tel").click()
    driver.find_element_by_id("tel").clear()
    driver.find_element_by_id("tel").send_keys(tel)
    driver.find_element_by_id("password").click()
    driver.find_element_by_id("password").clear()
    driver.find_element_by_id("password").send_keys(password)
    driver.find_element_by_id("password2").click()
    driver.find_element_by_id("password2").clear()
    driver.find_element_by_id("password2").send_keys(password2)
    driver.find_element_by_id("submit").click()


def ui_login_user(driver, email="ksun@ligang.net", username='leigong', password='123456'):
    """UI测试用户登录"""
    driver.get("http://127.0.0.1:5000/")
    driver.find_element_by_link_text("Login").click()
    driver.find_element_by_id("email").click()
    driver.find_element_by_id("email").clear()
    driver.find_element_by_id("email").send_keys(email)
    driver.find_element_by_id("password").click()
    driver.find_element_by_id("password").clear()
    driver.find_element_by_id("password").send_keys(password)
    driver.find_element_by_id("remember_me").click()
    driver.find_element_by_id("submit").click()


def ui_logout_user(driver):
    """UI测试用户登出"""
    driver.get("http://127.0.0.1:5000/")
    try:
        driver.find_element_by_css_selector("img.avatar-xs").click()
        driver.find_element_by_link_text("Logout").click()
    except NoSuchElementException as e:  # 未登录
        driver.get("http://127.0.0.1:5000/")
    finally:
        assert 'Join YouGuoQi' in driver.page_source


def ui_start_chat(driver, username2):
    driver.find_element_by_css_selector("img.avatar-xs").click()
    driver.find_element_by_link_text("My Home").click()
    driver.find_element_by_partial_link_text("Following").click()  # 查看用户关注者
    driver.find_element_by_css_selector('a[href = "/user/' + username2 + '"]').click()  # 访问关注者主页

    driver.find_element_by_id("start chat").click()  # 与用户2开始聊天
    time.sleep(5)


def ui_sent_message(driver, message):
    driver.find_element_by_id("message-textarea").click()
    driver.find_element_by_id("message-textarea").clear()
    driver.find_element_by_id("message-textarea").send_keys(message)
    driver.find_element_by_id("group-meg-submit").click()


def ui_enter_group(driver, room_name):
    """进入群聊"""
    driver.find_element_by_css_selector("span.oi.oi-bell").click()  # 打开通知页面
    driver.find_element_by_link_text(room_name).click()  # 进入群聊
    time.sleep(5)


def ui_buy(driver, dish_id, number, fare):
    driver.get("http://127.0.0.1:5000/dish/"+str(dish_id))
    driver.find_element_by_css_selector("span.oi.oi-cart").click()  # 单击购买
    driver.find_element_by_id("number").click()
    driver.find_element_by_id("number").clear()
    driver.find_element_by_id("number").send_keys(str(number))
    driver.find_element_by_id("fare").click()
    driver.find_element_by_id("fare").clear()
    driver.find_element_by_id("fare").send_keys(str(fare))
    driver.find_element_by_id("submit").click()


