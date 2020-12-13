from app.post import post_bp
from app import db
from datetime import datetime
from flask import render_template, redirect, url_for, flash, request
from flask_login import current_user, login_required
from .forms import PostCreationForm, PostEditingForm
from ..models import Post

ROWS_PER_PAGE = 5



@post_bp.route('/')
def posts():
    q = request.args.get('q')
    page = request.args.get('page', 1, type=int)
    if q:
        posts = Post.query.filter(Post.title.contains(q) | Post.body.contains(q))
    else:
        posts = Post.query.order_by(Post.timestamp.desc())

    pages = posts.paginate(page=page, per_page=ROWS_PER_PAGE)
    return render_template('posts.html', posts=posts, pages=pages, q=q)


@post_bp.route('/post/<int:id>')
def post(id):
    post = Post.query.filter_by(id=id).first()
    return render_template('post.html', post=post)


@post_bp.route('/create_post', methods=['GET', 'POST'])
@login_required
def create_post():
    form = PostCreationForm()
    if form.validate_on_submit():
        post_title = form.post_title.data
        post_body = form.post_body.data

        post = Post(title=post_title, body=post_body, author=current_user)

        db.session.add(post)
        db.session.commit()
        flash("Post created successfully")
        return redirect(url_for('post_bp.posts'))
    return render_template('create_post.html', form=form)


@post_bp.route('/edit_post/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_post(id):
    form = PostEditingForm()
    post = Post.query.filter_by(id=id).first()
    if form.validate_on_submit():
        if current_user.username != post.author.username:
            return redirect(url_for('main'))
        post.title = form.post_title.data
        post.body = form.post_body.data
        post.update_time = datetime.utcnow()

        db.session.commit()
        flash("Post edited successfully")
        return redirect(url_for('post_bp.posts'))


    elif request.method == 'GET':
        if current_user.username != post.author.username:
            return redirect(url_for('main'))
        form.post_title.data = post.title
        form.post_body.data = post.body
    return render_template('edit_post.html', form=form, post=post)


@post_bp.route('/delete_post/<int:id>', methods=["GET", "DELETE"])
@login_required
def delete_post(id):
    post = Post.query.filter_by(id=id).first()
    if current_user.username != post.author.username:
        return redirect(url_for('main'))

    db.session.delete(post)
    db.session.commit()
    return redirect(url_for('post_bp.posts'))


@post_bp.before_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        db.session.commit()
