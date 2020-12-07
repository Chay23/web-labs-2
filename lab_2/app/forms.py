from flask import url_for, request, flash
from flask_admin import AdminIndexView
from flask_admin.contrib.sqla import ModelView
from flask_admin.form import rules
from flask_login import current_user
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from werkzeug.utils import redirect
from wtforms import StringField, PasswordField, SubmitField, BooleanField, TextAreaField, widgets
from wtforms.validators import DataRequired, Email, Length, EqualTo, ValidationError, Regexp
from wtforms.widgets import TextArea

from app import bcrypt
from app.models import User


class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign in')


class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[Length(min=4, max=25,
                                                          message="Username length should be between 4 and 25"),
                                                   DataRequired(message="This field can't be empty"),
                                                   Regexp('^[A-Za-z][A-Za-z0-9_.]*$', 0,
                                                          'Username must have only '
                                                          'letters, numbers, dots or '
                                                          'underscores')])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password',
                             validators=[Length(min=6, message="Length of password should be greater than 6")])
    password_confirm = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Sing up')

    def validate_email(self, field):
        if User.query.filter_by(email=field.data).first():
            raise ValidationError('Email already registered')

    def validate_username(self, field):
        if User.query.filter_by(username=field.data).first():
            raise ValidationError('Username already registered')


class UpdateAccountForm(FlaskForm):
    username = StringField('Username', validators=[Length(min=4, max=25,
                                                          message="Username length should be between 4 and 25"),
                                                   DataRequired(message="This field can't be empty"),
                                                   Regexp('^[A-Za-z][A-Za-z0-9_.]*$', 0,
                                                          'Username must have only '
                                                          'letters, numbers, dots or '
                                                          'underscores')])
    email = StringField('Email', validators=[DataRequired(), Email()])
    picture = FileField('Update Profile Picture', validators=[FileAllowed(['jpg', 'png'])])
    about_me = TextAreaField('About me', render_kw={'rows': 5}, validators=[Length(min=0, max=50)])
    old_password = PasswordField('Old password')
    new_password = PasswordField('New password')
    confirm_new_password = PasswordField('Confirm new password')
    submit = SubmitField('Update')

    def validate_email(self, email):
        if email.data != current_user.email:
            user = User.query.filter_by(email=email.data).first()
            if user:
                raise ValidationError('Email already registered')

    def validate_username(self, username):
        if username.data != current_user.username:
            user = User.query.filter_by(username=username.data).first()
            if user:
                raise ValidationError('Username already registered')

    def validate_old_password(self, old_password):
        if self.old_password.data:
            if not bcrypt.check_password_hash(current_user.password_hash, self.old_password.data):
                raise ValidationError('Wrong old password')

    def validate_confirm_new_password(self, confirm_new_password):
        if self.old_password.data:
            if self.new_password.data != self.confirm_new_password.data:
                raise ValidationError('New password didn\'t match')


class PostCreationForm(FlaskForm):
    post_title = StringField('Post title', validators=[DataRequired()])
    post_body = TextAreaField('Post body', render_kw={'rows': 5}, validators=[DataRequired()])
    submit = SubmitField('Create')


class PostEditingForm(FlaskForm):
    post_title = StringField('Post title', validators=[DataRequired()])
    post_body = TextAreaField('Post body', render_kw={'rows': 5}, validators=[DataRequired()])
    submit = SubmitField('Edit')


class MyIndexView(AdminIndexView):
    def is_accessible(self):
        return current_user.is_authenticated and current_user.is_admin()

    def inaccessible_callback(self, name, **kwargs):
        # redirect to login page if user doesn't have access
        return redirect(url_for('login', next=request.url))


class MyAccessModelView(ModelView):
    def is_accessible(self):
        return current_user.is_authenticated and current_user.is_admin()

    def inaccessible_callback(self, name, **kwargs):
        # redirect to login page if user doesn't have access
        return redirect(url_for('login', next=request.url))


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
        'username', 'email',  'password', 'image_file', 'about_me', 'admin'
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


class AdminUserCreateForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    admin = BooleanField('Is Admin ?')
    submit = SubmitField('Create')


class AdminUserUpdateForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired()])
    admin = BooleanField('Is Admin ?')
    submit = SubmitField('Update')
