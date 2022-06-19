import mimetypes
import os
import uuid
import filetype
import cloudinary
from cloudinary.uploader import upload
from bleach import clean, linkify
from markdown import markdown

try:
    from urlparse import urlparse, urljoin
except ImportError:
    from urllib.parse import urlparse, urljoin


import PIL
from PIL import Image
from flask import current_app, request, url_for, redirect, flash
from itsdangerous import BadSignature, SignatureExpired
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer

from .extensions import db, avatars
from .models import User
from .settings import Operations


def is_image(filetype):
    kind = mimetypes.types_map[filetype]
    return kind.split('/')[0] == 'image'


def upload_cloudinary(file_to_upload):
    cloudinary.config(cloud_name=os.getenv('CLOUD_NAME'), api_key=os.getenv('API_KEY'),
                      api_secret=os.getenv('API_SECRET'))
    upload_result = upload(file_to_upload)
    file_url, options = cloudinary.utils.cloudinary_url(
        upload_result['public_id'],
        format=upload_result['format'],
        crop="fill")
    return file_url, upload_result['format']


def crop_img(filename, x, y, w, h):
    x = int(x)
    y = int(y)
    w = int(w)
    h = int(h)

    sizes = current_app.config['AVATARS_SIZE_TUPLE']

    raw_img = Image.open(filename)

    base_width = current_app.config['AVATARS_CROP_BASE_WIDTH']

    if raw_img.size[0] >= base_width:
        raw_img = avatars.resize_avatar(raw_img, base_width=base_width)

    cropped_img = raw_img.crop((x, y, x + w, y + h))

    avatar_s = avatars.resize_avatar(cropped_img, base_width=sizes[0])
    avatar_m = avatars.resize_avatar(cropped_img, base_width=sizes[1])
    avatar_l = avatars.resize_avatar(cropped_img, base_width=sizes[2])

    avatar_s.save(filename, optimize=True, quality=85)
    filename_s, filetype = upload_cloudinary(filename)
    avatar_m.save(filename, optimize=True, quality=85)
    filename_m, filetype = upload_cloudinary(filename)
    avatar_l.save(filename, optimize=True, quality=85)
    filename_l, filetype = upload_cloudinary(filename)

    return [filename_s, filename_m, filename_l]


def generate_token(user, operation, expire_in=None, **kwargs):
    """令牌生成函数"""
    s = Serializer(current_app.config['SECRET_KEY'], expire_in)

    data = {'id': user.id, 'operation': operation}
    data.update(**kwargs)
    return s.dumps(data)


def validate_token(user, token, operation, new_password=None):
    s = Serializer(current_app.config['SECRET_KEY'])

    try:
        data = s.loads(token)
    except (SignatureExpired, BadSignature):
        return False

    if operation != data.get('operation') or user.id != data.get('id'):
        return False

    if operation == Operations.CONFIRM:
        user.confirmed = True
    elif operation == Operations.RESET_PASSWORD:
        user.set_password(new_password)
    elif operation == Operations.CHANGE_EMAIL:
        new_email = data.get('new_email')
        if new_email is None:
            return False
        if User.query.filter_by(email=new_email).first() is not None:
            return False
        user.email = new_email
    else:
        return False

    db.session.commit()
    return True


def rename_file(old_filename):
    """重命名文件"""
    ext = os.path.splitext(old_filename)[1]
    new_filename = uuid.uuid4().hex + ext
    return new_filename


def resize_image(image, filename, base_width):
    """缩放图片"""
    filename, ext = os.path.splitext(filename)
    img = Image.open(image)
    if img.size[0] <= base_width:
        return filename + ext
    w_percent = (base_width / float(img.size[0]))
    h_size = int((float(img.size[1]) * float(w_percent)))
    img = img.resize((base_width, h_size), PIL.Image.ANTIALIAS)

    filename += current_app.config['YGQ_DISH_SUFFIX'][base_width] + ext
    img.save(os.path.join(current_app.config['YGQ_UPLOAD_PATH'], filename), optimize=True, quality=85)
    return filename


def is_safe_url(target):
    ref_url = urlparse(request.host_url)  # url获取程序内的主机URL
    test_url = urlparse(urljoin(request.host_url, target))  # 将目标URL转换为绝对URL
    return test_url.scheme in ('http', 'https') and \
           ref_url.netloc == test_url.netloc


def redirect_back(default='main.index', **kwargs):
    for target in request.args.get('next'), request.referrer:
        if not target:
            continue
        if is_safe_url(target):
            return redirect(target)
    return redirect(url_for(default, **kwargs))


def flash_errors(form):
    """闪现错误消息"""
    for field, errors in form.errors.items():
        for error in errors:
            flash(u"Error in the %s field - %s" % (
                getattr(form, field).label.text,
                error
            ))


def to_html(raw):
    allowed_tags = ['a', 'abbr', 'b', 'br', 'blockquote', 'code',
                    'del', 'div', 'em', 'img', 'p', 'pre', 'strong',
                    'span', 'ul', 'li', 'ol']
    allowed_attributes = ['src', 'title', 'alt', 'href', 'class']
    html = markdown(raw, output_format='html',
                    extensions=['markdown.extensions.fenced_code',
                                'markdown.extensions.codehilite'])
    clean_html = clean(html, tags=allowed_tags, attributes=allowed_attributes)
    return linkify(clean_html)