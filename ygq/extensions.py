from flask_avatars import Avatars
from flask_bootstrap import Bootstrap
from flask_cors import CORS
from flask_dropzone import Dropzone
from flask_login import LoginManager, AnonymousUserMixin
from flask_mail import Mail
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from flask_whooshee import Whooshee
from flask_wtf import CSRFProtect
from flask_socketio import SocketIO


bootstrap = Bootstrap()
db = SQLAlchemy()
login_manager = LoginManager()
mail = Mail()
dropzone = Dropzone()
moment = Moment()
whooshee = Whooshee()
avatars = Avatars()
csrf = CSRFProtect()
socketio = SocketIO()
cors = CORS()


@login_manager.user_loader
def load_user(user_id):
    from .models import User
    user = User.query.get(int(user_id))
    return user


login_manager.login_view = 'auth.login'
login_manager.login_message = 'Please log in to access this page.'
login_manager.login_message_category = 'warning'

login_manager.refresh_view = 'auth.re_authenticate'
login_manager.needs_refresh_message = '为了保护你的账户安全，请重新登录。'
login_manager.needs_refresh_message_category = 'warning'


class Guest(AnonymousUserMixin):
    """访客(使得未登录用户也有can和is_admin方法)"""
    def can(self, permission_name):
        return False

    @property
    def is_admin(self):
        return False


login_manager.anonymous_user = Guest  # 继承自匿名用户类


