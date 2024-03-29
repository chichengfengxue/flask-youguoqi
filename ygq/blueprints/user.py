import os

from flask import render_template, flash, redirect, url_for, current_app, request, Blueprint, abort, session
from flask_cors import cross_origin
from flask_login import login_required, current_user, fresh_login_required
from flask_socketio import rooms

from ..decorators import confirm_required
from ..emails import send_change_email_email
from ..extensions import db, avatars
from ..forms.user import EditProfileForm, UploadAvatarForm, CropAvatarForm, ChangeEmailForm, \
    ChangePasswordForm, DeleteAccountForm, EditOrder
from ..models import User, Rider, Dish, Order, Collect, Room
from ..notifications import push_new_order_notification, push_new_group_notification, push_group_notification
from ..settings import Operations
from ..utils import generate_token, validate_token, redirect_back, flash_errors, upload_cloudinary, rename_file, \
    crop_img
from sqlalchemy.sql.expression import func
from datetime import datetime, timedelta


user_bp = Blueprint('user', __name__)


@user_bp.route('/<username>', methods=['GET'])
def index(username):
    user = User.query.filter_by(username=username).first_or_404()
    page = request.args.get('page', 1, type=int)
    per_page = current_app.config['YGQ_DISH_PER_PAGE']
    pagination = Order.query.with_parent(user).order_by(Order.start_time.desc()).paginate(page, per_page)
    orders = pagination.items
    return render_template('user/index.html', user=user, pagination=pagination, orders=orders)


@user_bp.route('/buy/<int:dish_id>', methods=['GET', 'POST'])
@login_required
@confirm_required
def buy(dish_id):
    user = current_user
    dish = Dish.query.get_or_404(dish_id)
    form = EditOrder()
    if form.validate_on_submit():
        fare = int(form.fare.data)
        number = int(form.number.data)
        price = number*dish.price+fare+1
        order = Order(
            dish=dish,
            shop=dish.shop,
            consumer=user,
            fare=fare,
            number=number,
            price=price
        )
        db.session.add(order)
        db.session.commit()
        flash('Successfully ordered!', 'success')

        push_new_order_notification(order, order.shop.user)
        return redirect(url_for('.show_order', order_id=order.id))
    return render_template('user/buy.html', form=form)


@user_bp.route('/order/<int:order_id>', methods=['GET'])
@login_required
def show_order(order_id):
    order = Order.query.get_or_404(order_id)
    if current_user == order.shop.user or current_user == order.consumer:
        return render_template('user/show_order.html', order=order)
    elif order.rider:
        if current_user == order.rider.user:
            return render_template('user/show_order.html', order=order)
    else:
        abort(403)


@user_bp.route('/<username>/collections', methods=['GET'])
def show_collections(username):
    user = User.query.filter_by(username=username).first_or_404()
    page = request.args.get('page', 1, type=int)
    per_page = current_app.config['YGQ_DISH_PER_PAGE']
    pagination = Collect.query.with_parent(user).order_by(Collect.timestamp.desc()).paginate(page, per_page)
    collects = pagination.items
    return render_template('user/collections.html', user=user, pagination=pagination, collects=collects)


@user_bp.route('/follow/<username>', methods=['POST'])
@login_required
@confirm_required
def follow(username):
    user = User.query.filter_by(username=username).first_or_404()
    if current_user.is_following(user):
        flash('Already followed.', 'info')
        return redirect(url_for('.index', username=username))

    current_user.follow(user)
    flash('User followed.', 'success')
    return redirect_back()


@user_bp.route('/group/start/<username>', methods=['POST'])
@login_required
@confirm_required
def start_group(username):
    """发起聊天"""
    user = User.query.filter_by(username=username).first_or_404()
    room = Room(name=current_user.username+' and '+username+' \'s group')
    db.session.add(room)
    db.session.commit()
    session['username'] = username
    session['room'] = room.id
    push_new_group_notification(current_user.username, room.id, user)
    push_group_notification(room.id, current_user._get_current_object())
    return redirect(url_for('group.home', room_id=room.id))


@user_bp.route('/unfollow/<username>', methods=['POST'])
@login_required
def unfollow(username):
    user = User.query.filter_by(username=username).first_or_404()
    if not current_user.is_following(user):
        flash('Not follow yet.', 'info')
        return redirect(url_for('.index', username=username))

    current_user.unfollow(user)
    flash('User unfollowed.', 'info')
    return redirect_back()


@user_bp.route('/<username>/followers', methods=['GET'])
def show_followers(username):
    user = User.query.filter_by(username=username).first_or_404()
    page = request.args.get('page', 1, type=int)
    per_page = current_app.config['YGQ_USER_PER_PAGE']
    pagination = user.following.paginate(page, per_page)
    follows = pagination.items
    return render_template('user/following.html', user=user, pagination=pagination, follows=follows)


@user_bp.route('/settings/profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm()
    if form.validate_on_submit():
        current_user.name = form.name.data
        current_user.username = form.username.data
        current_user.location_x = form.location_x.data
        current_user.location_y = form.location_y.data
        current_user.tel = form.tel.data
        db.session.commit()
        flash('Profile updated.', 'success')
        return redirect(url_for('.index', username=current_user.username))
    form.name.data = current_user.name
    form.username.data = current_user.username
    form.tel.data = current_user.tel
    form.location_x.data = current_user.location_x
    form.location_y.data = current_user.location_y
    return render_template('user/settings/edit_profile.html', form=form)


@user_bp.route('/settings/avatar')
@login_required
@confirm_required
def change_avatar():
    upload_form = UploadAvatarForm()
    crop_form = CropAvatarForm()
    return render_template('user/settings/change_avatar.html', upload_form=upload_form, crop_form=crop_form)


@user_bp.route('/settings/avatar/upload', methods=['POST'])
@cross_origin()
@login_required
@confirm_required
def upload_avatar():
    form = UploadAvatarForm()
    if form.validate_on_submit():
        image = form.image.data
        # filename = avatars.save_avatar(image)

        filename = rename_file(image.filename)
        image.save(os.path.join(current_app.config['YGQ_UPLOAD_PATH'], filename))
        current_user.avatar_s = os.path.join(current_app.config['YGQ_UPLOAD_PATH'], filename)
        db.session.commit()

        filename, filetype = upload_cloudinary(os.path.join(current_app.config['YGQ_UPLOAD_PATH'], filename))
        current_user.avatar_raw = filename
        db.session.commit()
        flash('Image uploaded, please crop.', 'success')
    flash_errors(form)
    return redirect(url_for('.change_avatar'))


@user_bp.route('/settings/avatar/crop', methods=['POST'])
@login_required
@confirm_required
def crop_avatar():
    form = CropAvatarForm()
    if form.validate_on_submit():
        x = form.x.data
        y = form.y.data
        w = form.w.data
        h = form.h.data
        filenames = crop_img(current_user.avatar_s, x, y, w, h)

        current_user.avatar_s = filenames[0]
        current_user.avatar_m = filenames[1]
        current_user.avatar_l = filenames[2]

        db.session.commit()
        flash('Avatar updated.', 'success')
    flash_errors(form)
    return redirect(url_for('.change_avatar'))


@user_bp.route('/settings/change-password', methods=['GET', 'POST'])
@fresh_login_required
def change_password():
    form = ChangePasswordForm()
    if form.validate_on_submit():
        if current_user.validate_password(form.old_password.data):
            current_user.set_password(form.password.data)
            db.session.commit()
            flash('Password updated.', 'success')
            return redirect(url_for('.index', username=current_user.username))
        else:
            flash('Old password is incorrect.', 'warning')
    return render_template('user/settings/change_password.html', form=form)


@user_bp.route('/settings/change-email', methods=['GET', 'POST'])
@fresh_login_required
def change_email_request():
    form = ChangeEmailForm()
    if form.validate_on_submit():
        token = generate_token(user=current_user, operation=Operations.CHANGE_EMAIL, new_email=form.email.data.lower())
        send_change_email_email(to=form.email.data, user=current_user, token=token)
        flash('Confirm email sent, check your inbox.', 'info')
        return redirect(url_for('.index', username=current_user.username))
    return render_template('user/settings/change_email.html', form=form)


@user_bp.route('/change-email/<token>')
@login_required
def change_email(token):
    if validate_token(user=current_user, token=token, operation=Operations.CHANGE_EMAIL):
        flash('Email updated.', 'success')
        return redirect(url_for('.index', username=current_user.username))
    else:
        flash('Invalid or expired token.', 'warning')
        return redirect(url_for('.change_email_request'))


@user_bp.route('/settings/account/delete', methods=['GET', 'POST'])
def delete_account():
    form = DeleteAccountForm()
    if form.validate_on_submit():
        db.session.delete(current_user._get_current_object())
        db.session.commit()
        flash('Your are free, goodbye!', 'success')
        return redirect(url_for('main.index'))
    return render_template('user/settings/delete_account.html', form=form)
