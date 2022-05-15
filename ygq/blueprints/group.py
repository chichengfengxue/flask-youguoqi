from flask import render_template, redirect, url_for, request, Blueprint, current_app, abort, flash, session
from flask_login import current_user, login_required
from flask_socketio import emit, join_room, leave_room, rooms

from ..decorators import confirm_required
from ..extensions import socketio, db
from ..models import Message, User, Dish, Room
from ..utils import to_html

group_bp = Blueprint('group', __name__)


@group_bp.route('/<int:room_id>', methods=['GET'])
@login_required
@confirm_required
def home(room_id):
    session['username'] = current_user.username
    session['room'] = room_id
    room = Room.query.get_or_404(room_id)
    amount = current_app.config['YGQ_MESSAGE_PER_PAGE']
    messages = Message.query.filter_by(room=room).order_by(Message.timestamp.asc())[-amount:]
    return render_template('group/home.html', messages=messages, room=room.id, users=rooms(sid=room_id, namespace='/group'))


@group_bp.route('/messages/<int:room_id>', methods=['GET'])
@login_required
@confirm_required
def get_messages(room_id):
    """返回分页消息记录"""
    room = Room.query.get_or_404(room_id)
    page = request.args.get('page', 1, type=int)
    pagination = Message.query.filter_by(room=room).order_by(Message.timestamp.desc()).paginate(
        page, per_page=current_app.config['YGQ_MESSAGE_PER_PAGE'])
    messages = pagination.items
    return render_template('group/_messages.html', messages=messages[::-1])


@socketio.on('join', namespace='/group')
@login_required
@confirm_required
def on_join():
    """加入房间"""
    username = session.get("username")
    room = session.get("room")
    user = User.query.filter_by(username=username).first_or_404()
    room = Room.query.get_or_404(room)
    user.room = room
    db.session.commit()

    join_room(room.id)
    html_message = to_html(username + ' 进入房间。')
    message = Message(author=current_user._get_current_object(),
                      body=html_message,
                      room=room)
    db.session.add(message)
    db.session.commit()

    emit('status',
         {'message_html': render_template('group/_message.html', message=message),
          'message_body': html_message,
          'avatar_raw': current_user.avatar_raw,
          'name': current_user.name,
          'user_id': current_user.id},
         room=room.id,
         namespace='/group')  # 状态信息


@socketio.on('leave', namespace='/group')
@login_required
@confirm_required
def on_leave():
    """退出房间"""
    username = session.get("username")
    room = session.get("room")
    user = User.query.filter_by(username=username).first_or_404()
    room = Room.query.get_or_404(room)

    leave_room(room.id)
    html_message = to_html(username + ' 离开房间。')
    message = Message(author=current_user._get_current_object(),
                      body=html_message,
                      room=room)
    db.session.add(message)
    db.session.commit()
    emit('status',
         {'message_html': render_template('group/_message.html', message=message),
          'message_body': html_message,
          'avatar_raw': current_user.avatar_raw,
          'name': current_user.name,
          'user_id': current_user.id},
         room=room.id,
         namespace='/group')  # 状态信息


@socketio.on('room_message', namespace='/group')
@confirm_required
def new_room_message(message_body, room_id):
    room = Room.query.get_or_404(room_id)
    html_message = to_html(message_body)
    message = Message(author=current_user._get_current_object(),
                      body=html_message,
                      room=room)
    db.session.add(message)
    db.session.commit()

    emit('new room message',
         {'message_html': render_template('group/_message.html', message=message),
          'message_body': html_message,
          'avatar_raw': current_user.avatar_raw,
          'name': current_user.name,
          'user_id': current_user.id},
         room=room_id,
         namespace='/group')

