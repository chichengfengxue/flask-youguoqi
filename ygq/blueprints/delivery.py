from flask import render_template, redirect, url_for, request, Blueprint, current_app, abort, flash
from flask_login import current_user, login_required
from flask_socketio import emit
from sqlalchemy import and_

from ..decorators import confirm_required
from ..extensions import socketio, db
from ..models import Message, User, Dish, Order
from ..utils import to_html

delivery_bp = Blueprint('delivery', __name__)


@delivery_bp.route('/')
@login_required
def home():
    amount = current_app.config['YGQ_MESSAGE_PER_PAGE']
    orders = Order.query.filter_by(is_accept=False).order_by(Order.start_time.asc())[-amount:]
    current_order = Order.query.filter(and_(Order.consumer_id == current_user.id, Order.is_accept == False)).first()
    return render_template('delivery/home.html', orders=orders, current_order=current_order)


@delivery_bp.route('/orders')
@login_required
def get_orders():
    """返回分页订单记录"""
    page = request.args.get('page', 1, type=int)
    pagination = Order.query.filter_by(is_accept=False).order_by(Order.start_time.desc()).paginate(
        page, per_page=current_app.config['YGQ_MESSAGE_PER_PAGE'])
    orders = pagination.items
    return render_template('delivery/_deliveries.html', orders=orders[::-1])


@delivery_bp.route('/delivery/accept/<int:order_id>', methods=['GET'])
@login_required
@confirm_required
def accept_delivery(order_id):
    order = Order.query.get_or_404(order_id)
    order.is_accept = True
    order.rider = current_user.rider[0]
    db.session.commit()
    return '', 204


@socketio.on('new delivery', namespace='/delivery')
@login_required
def new_delivery(order_id, fare):
    """new delivery事件处理函数"""
    order = Order.query.get_or_404(order_id)
    if current_user.id != order.consumer_id or order.is_accept:
        abort(403)
    order.fare = int(fare)
    db.session.commit()

    emit('new delivery',
         {'message_html': render_template('delivery/_delivery.html', order=order),
          'avatar_raw': current_user.avatar_raw,
          'name': current_user.name,
          'user_id': current_user.id},
         broadcast=True, namespace='/delivery')
