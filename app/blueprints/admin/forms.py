from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, BooleanField, SubmitField, PasswordField, IntegerField, FloatField, TextAreaField, FileField
from wtforms.validators import Email, DataRequired, EqualTo
import email_validator


###############################
# COURSES OBJECTIVES
###############################
class AdminCreateObjective(FlaskForm):
    description = TextAreaField(validators=[DataRequired()])
    submit = SubmitField('Create Objective')
###############################
# COURSES OBJECTIVES
###############################

###############################
# COURSES
###############################
class AdminCreateCourseForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    description = TextAreaField('Description', validators=[DataRequired()])
    image = FileField('Upload Image', validators=[DataRequired()])
    video = FileField('Upload Video', validators=[DataRequired()])
    icon = StringField('Icon', validators=[DataRequired()])
    category = SelectField(choices=[], coerce=int)
    skill_level = SelectField(choices=[], coerce=int)
    submit = SubmitField('Create Course')

# TODO: UNDERNEATH
# class AdminCreateCourseForm(FlaskForm):
#     name = StringField('Name', validators=[DataRequired()])
#     icon = StringField('Icon', validators=[DataRequired()])
#     submit = SubmitField('Edit Course')
    
class AdminEditCourseForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    description = TextAreaField('Description', validators=[DataRequired()])
    skill_level = SelectField(choices=[], coerce=int)
    icon = StringField('Icon', validators=[DataRequired()])
    video = FileField('Upload Video')
    video_thumbnail = FileField('Upload Video Thumbnail')
    category = SelectField(choices=[], coerce=int)
    video_verify = BooleanField('Click to verify video upload.')
    video_thumbnail_verify = BooleanField('Click to verify video thumbnail upload.')
    tags = TextAreaField('Tags')
    submit = SubmitField('Edit Course')
###############################
# COURSES
###############################

###############################
# COURSE CATEGORY
###############################
class AdminEditCourseCategoryForm(FlaskForm):
    name = StringField('Name')
    # name = StringField('Name', validators=[DataRequired()])
    image = FileField('Upload Image')
    image_verify = BooleanField('Click to verify upload.')
    # icon = StringField('Icon', validators=[DataRequired()])
    icon = StringField('Icon')
    submit = SubmitField('Edit Course Category')


class AdminCreateCourseCategoryForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    image = FileField('Upload Image', validators=[DataRequired()])
    icon = StringField('Icon', validators=[DataRequired()])
    submit = SubmitField('Create Course Category')
###############################
# COURSE CATEGORY
###############################

class AdminUserForm(FlaskForm):
    email = StringField(validators=[Email()])
    first_name = StringField('First Name', validators=[DataRequired()])
    last_name = StringField('Last Name', validators=[DataRequired()])
    role = SelectField(choices=[], coerce=int)
    # is_admin = BooleanField('is_admin')
    submit = SubmitField('Create User')

class AdminLoginForm(FlaskForm):
    email = StringField('Email', validators=[Email(), DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember password')
    submit = SubmitField('Login')

class AdminEditUserForm(FlaskForm):
    email = StringField(validators=[Email()])
    first_name = StringField('First Name', validators=[DataRequired()])
    last_name = StringField('Last Name', validators=[DataRequired()])
    role = SelectField(choices=[], coerce=int)
    is_admin = BooleanField('is_admin')
    submit = SubmitField('Update User')
    
class AdminResetPasswordRequestForm(FlaskForm):
    email = StringField('Email', validators=[Email(), DataRequired()])
    submit = SubmitField('Request Password Reset')

class AdminResetPasswordForm(FlaskForm):
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Reset Password')