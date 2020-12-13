from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField
from wtforms.validators import DataRequired


class PostCreationForm(FlaskForm):
    post_title = StringField('Post title', validators=[DataRequired()])
    post_body = TextAreaField('Post body', render_kw={'rows': 5}, validators=[DataRequired()])
    submit = SubmitField('Create')


class PostEditingForm(FlaskForm):
    post_title = StringField('Post title', validators=[DataRequired()])
    post_body = TextAreaField('Post body', render_kw={'rows': 5}, validators=[DataRequired()])
    submit = SubmitField('Edit')
