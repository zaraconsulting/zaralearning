from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, BooleanField, SubmitField, PasswordField, IntegerField, FloatField, TextAreaField, FileField
from wtforms.validators import Email, DataRequired, EqualTo
import email_validator

class AdminUserForm(FlaskForm):
    email = StringField(validators=[Email()])
    first_name = StringField('First Name', validators=[DataRequired()])
    last_name = StringField('Last Name', validators=[DataRequired()])
    role = SelectField(choices=[], coerce=int)
    # is_admin = BooleanField('is_admin')
    submit = SubmitField('Create User')

class AdminEditUserForm(FlaskForm):
    email = StringField(validators=[Email()])
    first_name = StringField('First Name', validators=[DataRequired()])
    last_name = StringField('Last Name', validators=[DataRequired()])
    role = SelectField(choices=[], coerce=int)
    is_admin = BooleanField('is_admin')
    submit = SubmitField('Update User')

class AdminLoginForm(FlaskForm):
    email = StringField('Email', validators=[Email(), DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember password')
    submit = SubmitField('Login')

class AdminCreateCourseForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    description = TextAreaField('Description', validators=[DataRequired()])
    image = FileField('Upload Image', validators=[DataRequired()])
    video = FileField('Upload Video', validators=[DataRequired()])
    icon = StringField('Icon', validators=[DataRequired()])
    category = SelectField(choices=[], coerce=int)
    submit = SubmitField('Create Course')
    
class AdminEditCourseCategoryForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    icon = StringField('Icon', validators=[DataRequired()])
    submit = SubmitField('Edit Course')
    
class AdminEditCourseForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    description = TextAreaField('Description', validators=[DataRequired()])
    icon = StringField('Icon', validators=[DataRequired()])
    video = StringField('Video')
    video_thumbnail = StringField('Thumbnail')
    category = SelectField(choices=[], coerce=int)
    tags = TextAreaField('Tags')
    submit = SubmitField('Edit Course')

class AdminCreateObjective(FlaskForm):
    description = TextAreaField(validators=[DataRequired()])
    submit = SubmitField('Create Objective')

class AdminCreateCourseCategoryForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    image = FileField('Upload Image', validators=[DataRequired()])
    icon = StringField('Icon', validators=[DataRequired()])
    submit = SubmitField('Create Course Category')

class AdminEditCourseCategoryForm(FlaskForm):
    name = StringField('Name')
    # name = StringField('Name', validators=[DataRequired()])
    image = FileField('Upload Image')
    image_verify = BooleanField('Click to verify upload.')
    # icon = StringField('Icon', validators=[DataRequired()])
    icon = StringField('Icon')
    submit = SubmitField('Edit Course Category')

class AdminResetPasswordRequestForm(FlaskForm):
    email = StringField('Email', validators=[Email(), DataRequired()])
    submit = SubmitField('Request Password Reset')

class AdminResetPasswordForm(FlaskForm):
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Reset Password')