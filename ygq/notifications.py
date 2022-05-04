from datetime import timedelta

from flask import url_for

from .extensions import db
from .models import Notification


def push_new_order_notification(order, receiver):
    """推送新订单消息"""
    message = '您有新的外卖订单 <a href="%s">%s</a> ! \n %s' % \
              (url_for('user.show_order', order_id=order.id), order.dish.name, order.start_time)
    notification = Notification(message=message, receiver=receiver, timestamp=order.start_time)
    db.session.add(notification)
    db.session.commit()


def push_delivered_notification(order):
    """推送订单已送达消息"""
    message = '您的外卖 <a href="%s">%s</a> 已送达! 祝您用餐愉快！\n %s' % \
              (url_for('user.show_order', order_id=order.id), order.dish.name, order.time)
    notification = Notification(message=message, receiver=order.consumer, timestamp=order.time)
    db.session.add(notification)
    db.session.commit()


def push_new_group_notification(username, room_id, receiver):
    """新会话通知"""
    message = '<a href="%s">%s</a> 邀请您加入<a href="%s"> 聊天 </a> !' % \
              (url_for('user.index', username=username), username, url_for('group.home', room_id=room_id))
    notification = Notification(message=message, receiver=receiver)
    db.session.add(notification)
    db.session.commit()


def push_group_notification(room_id, receiver):
    """会话记录"""
    message = '<a href="%s"> 聊天 </a> !' % (url_for('group.home', room_id=room_id))
    notification = Notification(message=message, receiver=receiver)
    db.session.add(notification)
    db.session.commit()
