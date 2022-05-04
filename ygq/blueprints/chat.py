from flask import render_template, redirect, url_for, request, Blueprint, current_app, abort, flash
from flask_login import current_user, login_required
from flask_socketio import emit

from ..extensions import socketio, db
from ..models import Message, User, Dish
from ..utils import to_html

chat_bp = Blueprint('chat', __name__)

online_users = []


@socketio.on('new message')
@login_required
def new_message(message_body, dish_id=None):
    """new message事件处理函数"""
    html_message = to_html(message_body)
    dish = None
    if dish_id:
        dish = Dish.query.get_or_404(dish_id)
    message = Message(author=current_user._get_current_object(), body=html_message, dish=dish)
    db.session.add(message)
    db.session.commit()

    emit('new message',
         {'message_html': render_template('chat/_message.html', message=message, dish=dish),
          'message_body': html_message,
          'avatar_raw': current_user.avatar_raw,
          'name': current_user.name,
          'user_id': current_user.id},
         broadcast=True)


@chat_bp.route('/')
@login_required
def home():
    amount = current_app.config['YGQ_MESSAGE_PER_PAGE']
    messages = Message.query.filter_by(room_id=0).order_by(Message.timestamp.asc())[-amount:]
    return render_template('chat/home.html', messages=messages)


@chat_bp.route('/messages')
@login_required
def get_messages():
    """返回分页消息记录"""
    page = request.args.get('page', 1, type=int)
    pagination = Message.query.filter_by(room_id=0).order_by(Message.timestamp.desc()).paginate(
        page, per_page=current_app.config['YGQ_MESSAGE_PER_PAGE'])
    messages = pagination.items
    return render_template('chat/_messages.html', messages=messages[::-1])

