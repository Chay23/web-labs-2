import datetime as dt
from datetime import datetime
from functools import wraps

import jwt
from flask import jsonify, request

import config
from app import db, bcrypt
from app.api_post import api_post_bp
from ..models import Post_API, User


def token_required(f):
    @wraps(f)
    def decorator(*args, **kwargs):

        token = None

        if 'x-access-tokens' in request.headers:
            token = request.headers['x-access-tokens']

        if not token:
            return jsonify({'details': 'A valid token is missing'})

        try:
            data = jwt.decode(token, config.Config.SECRET_KEY)
            current_user = User.query.filter_by(id=data['id']).first()
        except:
            return jsonify({'details': 'Token is invalid'})

        return f(current_user, *args, **kwargs)

    return decorator


@api_post_bp.route('/token', methods=['GET', 'POST'])
def get_token():
    auth = request.authorization
    if not auth or not auth.username or not auth.password:
        return jsonify({'details': 'Invalid data'})
    user = User.query.filter_by(username=auth.username).first()

    if bcrypt.check_password_hash(user.password_hash, auth.password):
        token = jwt.encode(
            {'id': user.id, 'exp': datetime.utcnow() + dt.timedelta(hours=24)},
            config.Config.SECRET_KEY)
        return jsonify({'token': token.decode('UTF-8')})

    return jsonify({'details': 'Invalid data'})


@api_post_bp.route('posts/<int:post_id>', methods=['GET'])
@api_post_bp.route('posts', methods=['GET'])
@token_required
def api_get_posts(current_user, post_id=None):
    if post_id:
        post = Post_API.query.filter_by(id=post_id).first()
        print(post)
        if not post:
            return jsonify({"details": "Not found"})
        result = {'id': post.id,
                  'title': post.title,
                  'body': post.body,
                  'timestamp': post.timestamp,
                  'update_time': post.update_time,
                  'user_id': post.user_id
                  }
        return jsonify(result)
    else:
        posts = Post_API.query.all()
        result = []
        for post in posts:
            result.append({'id': post.id,
                           'title': post.title.strip(),
                           'body': post.body,
                           'timestamp': post.timestamp,
                           'update_time': post.update_time,
                           'user_id': post.user_id
                           })
        return jsonify(result)


@api_post_bp.route('posts', methods=['POST'])
@token_required
def api_create_post(current_user):
    post_data = request.json
    post = Post_API(title=post_data['title'], body=post_data['body'], user_id=current_user.id)
    db.session.add(post)
    db.session.commit()
    return jsonify({'details': 'Success'})


@api_post_bp.route('posts/<int:post_id>', methods=['PUT'])
@token_required
def api_edit_post(current_user, post_id):
    post = Post_API.query.filter_by(id=post_id).first()
    if post.user_id != current_user.id:
        return jsonify({'details': 'You are not author of this post'})
    elif not post:
        return jsonify({'details': 'Not found'})
    post_data = request.json
    post.title = post_data['title']
    post.body = post_data['body']
    post.update_time = datetime.utcnow()
    db.session.commit()
    return jsonify({'details': 'Success'})


@api_post_bp.route('posts/<int:post_id>', methods=['DELETE'])
@token_required
def api_delete_post(current_user, post_id):
    post = Post_API.query.filter_by(id=post_id).first()

    if not post:
        return jsonify({'detail': 'Not found'})
    else:
        db.session.delete(post)
        db.session.commit()
        return jsonify({'details': 'Success'})
