from app.post import post_bp
from functools import wraps

from flask import render_template, redirect, url_for, flash, request
from flask_login import current_user, logout_user, login_required

from app import bcrypt
from app import db
from app.custom_admin import custom_admin_bp
from .forms import AdminUserCreateForm, AdminUserUpdateForm
from ..models import User

ROWS_PER_PAGE = 5


def admin_login_required(func):
    @wraps(func)
    def check(*args, **kwargs):
        if current_user.is_admin():
            return func(*args, **kwargs)
        flash('You are not admin')
        return redirect(url_for('post_bp.posts'))

    return check


# Custom admin start
@custom_admin_bp.route('/admin_custom')
@login_required
@admin_login_required
def home_admin():
    return render_template('admin-home.html')


@custom_admin_bp.route('/admin_custom/users-list')
@login_required
@admin_login_required
def users_list_admin():
    users = User.query.all()
    return render_template('users-list-admin.html', users=users)


@custom_admin_bp.route('/admin_custom/create-user', methods=['GET', 'POST'])
@login_required
@admin_login_required
def user_create_admin():
    form = AdminUserCreateForm()

    if form.validate_on_submit():
        username = form.username.data
        email = form.email.data
        password = form.password.data
        admin = form.admin.data

        hashed = bcrypt.generate_password_hash(password).decode('utf-8')

        user = User(username=username, email=email, password_hash=hashed, admin=admin)
        db.session.add(user)
        db.session.commit()
        flash("Create successfully")
        return redirect(url_for('custom_admin_bp.users_list_admin'))
    return render_template('user-create-admin.html', form=form)


@custom_admin_bp.route('/admin_custom/update-user/<int:id>', methods=['GET', 'POST'])
@login_required
@admin_login_required
def user_update_admin(id):
    form = AdminUserUpdateForm()
    user = User.query.get(id)
    print(user)
    if form.validate_on_submit():
        user.username = form.username.data
        user.email = form.email.data
        user.admin = form.admin.data
        db.session.commit()
        flash('User has been updated!', 'success')
        return redirect(url_for('custom_admin_bp.users_list_admin'))
    elif request.method == 'GET':
        form.username.data = user.username
        form.email.data = user.email
        form.admin.data = user.admin
    return render_template('user-update-admin.html', form=form, user=user)


@custom_admin_bp.route('/admin_custom/delete/<int:id>')
@login_required
@admin_login_required
def user_delete_admin(id):
    user = User.query.get(id)
    db.session.delete(user)
    db.session.commit()
    flash('User Deleted.')
    return redirect(url_for('custom_admin_bp.users_list_admin'))


# Custom admin end

@custom_admin_bp.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('post_bp.posts'))
