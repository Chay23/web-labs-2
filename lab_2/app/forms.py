from flask import url_for, request, flash
from flask_admin import AdminIndexView
from flask_admin.contrib.sqla import ModelView
from flask_admin.form import rules
from flask_login import current_user
from werkzeug.utils import redirect
from wtforms import PasswordField, TextAreaField
from wtforms.widgets import TextArea

from app import bcrypt


class MyIndexView(AdminIndexView):
    def is_accessible(self):
        return current_user.is_authenticated and current_user.is_admin()

    def inaccessible_callback(self, name, **kwargs):
        # redirect to login page if user doesn't have access
        return redirect(url_for('user_bp.login', next=request.url))


class MyAccessModelView(ModelView):
    def is_accessible(self):
        return current_user.is_authenticated and current_user.is_admin()

    def inaccessible_callback(self, name, **kwargs):
        # redirect to login page if user doesn't have access
        return redirect(url_for('user_bp.login', next=request.url))


class UserAdminView(MyAccessModelView):
    column_searchable_list = ('username',)
    column_sortable_list = ('username', 'admin')
    column_exclude_list = ('about_me', 'last_seen')
    form_excluded_columns = ('password_hash', 'last_seen')
    form_edit_rules = ('username', 'admin')

    def scaffold_form(self):
        form_class = super(UserAdminView, self).scaffold_form()
        form_class.password = PasswordField('Password')
        form_class.new_password = PasswordField('New Password')
        form_class.confirm = PasswordField('Confirm New Password')
        return form_class

    def create_model(self, form):
        model = self.model(username=form.username.data, password_hash=bcrypt.generate_password_hash(form.password.data),
                           admin=form.admin.data
                           )
        form.populate_obj(model)
        self.session.add(model)
        self._on_model_change(form, model, True)
        self.session.commit()

    form_edit_rules = (
        'username', 'admin',
        rules.Header('Reset Password'),
        'new_password', 'confirm'
    )
    form_create_rules = (
        'username', 'email', 'password', 'image_file', 'about_me', 'admin'
    )

    def update_model(self, form, model):
        form.populate_obj(model)
        if form.new_password.data:
            if form.new_password.data != form.confirm.data:
                flash('Passwords must match')
                return
            model.password_hash = bcrypt.generate_password_hash(form.new_password.data)
        self.session.add(model)
        self._on_model_change(form, model, False)
        self.session.commit()


class CKTextAreaWidget(TextArea):
    def __call__(self, field, **kwargs):
        if kwargs.get('class'):
            kwargs['class'] += " ckeditor"
        else:
            kwargs.setdefault('class', 'ckeditor')
        return super(CKTextAreaWidget, self).__call__(field, **kwargs)


class CKTextAreaField(TextAreaField):
    widget = CKTextAreaWidget()


class PostModelView(MyAccessModelView):
    form_overrides = dict(body=CKTextAreaField)
    create_template = 'edit.html'
    edit_template = 'edit.html'

    column_exclude_list = ['timestamp', ]
    column_searchable_list = ['id', ]
    column_sortable_list = ('title', 'update_time')
    column_filters = ['title', 'timestamp']
