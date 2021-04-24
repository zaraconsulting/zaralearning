from .import bp as admin
from flask import render_template, redirect, url_for, request, flash, session, current_app as app, jsonify
from app.blueprints.courses.models import Course, CourseCategory, CourseTag, CourseLearningObjectives, SkillLevel
from app.blueprints.auth.models import Account
from .forms import AdminEditCourseCategoryForm, AdminCreateCourseCategoryForm, AdminLoginForm, AdminEditUserForm, AdminCreateCourseForm, AdminResetPasswordRequestForm, AdminResetPasswordForm, AdminEditCourseForm, AdminCreateObjective
from flask_login import current_user, login_user, logout_user
from app import db
import requests, stripe, time, boto3, os
from requests_toolbelt.multipart.encoder import MultipartEncoder
from datetime import datetime as dt
from werkzeug.utils import secure_filename
from botocore.exceptions import ClientError
from app._helpers import clear_temp_dir
from moviepy.editor import VideoFileClip

@admin.route('/', methods=['GET'])
def index():
    if not current_user.is_authenticated:
        return redirect(url_for('admin.login'))
    # else:
        # user = Account.query.get(current_user.id)
        # customer = stripe.Customer.retrieve(user.customer_id)
        # if user.is_customer:
        #     logout_user()
        #     return redirect(url_for('admin.login'))
    return render_template('admin/index.html')

@admin.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        logout_user()
        return redirect(url_for('admin.index'))
    form = AdminLoginForm()
    if form.validate_on_submit():
        email = form.email.data.lower()
        password = form.password.data

        user = Account.query.filter_by(email=email).first()
        if user is None or not user.check_password(password):
            flash('You have entered either an incorrect email or password. Try again.', 'danger')
            return redirect(url_for('admin.login'))
        # print(user.to_dict())
        login_user(user, remember=form.remember_me.data)
        flash('You have logged in successfully', 'success')
        return redirect(url_for('admin.index'))
    return render_template('admin/authentication/login.html', form=form)

@admin.route('/logout')
def logout():
    if not current_user.is_authenticated:
        return redirect(url_for('admin.login'))
    logout_user()
    flash('You have logged out successfully', 'info')
    return redirect(url_for('admin.index'))

@admin.route('/reset_password_request', methods=['GET', 'POST'])
def reset_password_request():
    if current_user.is_authenticated:
        return redirect(url_for('admin.index'))
    form = AdminResetPasswordRequestForm()
    if form.validate_on_submit():
        user = Account.query.filter_by(email=form.email.data.lower()).first()
        if not user:
            flash('Account holder with that email address was not found', 'warning')
            return redirect(url_for('admin.reset_password_request'))
        if user:
            send_password_reset_email(user)
            flash("Check your email for instructions to reset your password", 'primary')
            return redirect(url_for('admin.login'))
    return render_template('admin/authentication/reset_password_request.html', title='Reset Password', form=form)

@admin.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    if current_user.is_authenticated:
        return redirect(url_for('admin.index'))
    
    user = Account.verify_reset_password_token(token)
    # print(user)
    if not user:
        flash('Your password reset token is probably expired. Follow steps for resetting password again.', 'warning')
        return redirect(url_for('admin.login'))
    form = AdminResetPasswordForm()
    if form.validate_on_submit():
        # print(form.password.data)
        user.set_password(form.password.data)
        db.session.commit()
        flash('Your password has been reset', 'success')
        return redirect(url_for('admin.login'))
    return render_template('admin/reset_password.html', user=user, form=form)


@admin.route('/objective/course', methods=['GET', 'POST'])
def create_objective():
    form = AdminCreateObjective()
    if not current_user.is_authenticated:
        return redirect(url_for('admin.login'))
    if request.method == 'POST':
        o = CourseLearningObjectives(description=form.description.data, course_id=request.form.get('course_id'))
        o.save()
        flash('Course Learning Objective successfully added.', 'success')
        return redirect(url_for('admin.edit_course', id=request.form.get('course_id')))
    return render_template('admin/objective.html', form=form, course=Course.query.get(request.args.get('id')).to_dict())


@admin.route('/objective/delete', methods=['GET', 'POST'])
def delete_objective():
    if request.args:
        o = CourseLearningObjectives.query.get(request.args.get('objective_id'))
        if o is not None:
            o.delete()
        flash('Course Learning Objective successfully delete.', 'success')
        return redirect(url_for('admin.edit_course', id=request.args.get('course_id')))


@admin.route('/courses', methods=['GET'])
def courses():
    if not current_user.is_authenticated:
        return redirect(url_for('admin.login'))
    form = AdminCreateCourseForm()
    form.category.choices = [(i.id, i.name) for i in CourseCategory.query.all()]
    form.skill_level.choices = [(i.id, i.name) for i in SkillLevel.query.order_by(SkillLevel.name).all()]
    context = {
        'courses': [i.to_dict() for i in Course.query.all()],
        'form': form
    }
    return render_template('admin/courses.html', **context)

@admin.route('/course/edit', methods=['GET', 'POST'])
def edit_course():
    if not current_user.is_authenticated:
        return redirect(url_for('admin.login'))
    c = Course.query.get(request.args.get('id'))
    
    if request.method == 'GET':
        form = AdminEditCourseForm()
        
        form.category.choices = [(i.id, i.name) for i in CourseCategory.query.order_by(CourseCategory.name).all()]
        form.skill_level.choices = [(i.id, i.name) for i in SkillLevel.query.order_by(SkillLevel.name).all()]
        form.description.data = c.description
        form.category.data = c.category_id
        form.skill_level.data = c.skill_level_id
        form.tags.data = ', '.join([i.text for i in CourseTag.query.filter_by(course_id=c.id).all()])

    if request.method == 'POST':
        form = AdminEditCourseForm()
        
        # Connect to S3 client
        s3_client = boto3.client('s3', aws_access_key_id=app.config.get('AWS_ACCESS_KEY_ID'), aws_secret_access_key=app.config.get('AWS_SECRET_ACCESS_KEY'))
        
        data = dict(name=form.name.data, icon=form.icon.data, description=form.description.data, category_id=form.category.data, skill_level_id=form.skill_level.data)
        if form.video_verify.data:
            form.video.data.save(f"temp/{form.video.data.filename}")
            s3_client.upload_fileobj(open(f'temp/{form.video.data.filename}', 'rb'), app.config.get('AWS_S3_BUCKET'), 'courses/videos/' + form.video.data.filename, ExtraArgs={'ContentType': "video/mp4", 'ACL': 'public-read' })
            video_length = float(VideoFileClip(f"{app.config.get('BASEDIR')}/temp/{form.video.data.filename}").duration) / 60
            data['video'] = form.video.data.filename
            data['video_length'] = video_length
            os.remove(f'{app.config.get("BASEDIR")}/temp/{form.video.data.filename}')
        
        if form.video_thumbnail_verify.data:
            form.video_thumbnail.data.save(f"temp/{form.video_thumbnail.data.filename}")
            s3_client.upload_fileobj(open(f'temp/{form.video_thumbnail.data.filename}', 'rb'), app.config.get('AWS_S3_BUCKET'), 'courses/thumbnails/' + form.video_thumbnail.data.filename, ExtraArgs={'ContentType': "image/png", 'ACL': 'public-read' })
            data['video_thumbnail'] = form.video_thumbnail.data.filename
            os.remove(f'{app.config.get("BASEDIR")}/temp/{form.video_thumbnail.data.filename}')

        c.from_dict(data)
        
        [db.session.delete(i) for i in CourseTag.query.filter_by(course_id=c.id).all()]
        db.session.commit()

        tags = form.tags.data.lower().split(', ')
        # print(tags)
        new_tags = []
        for t in tags:
            tag = CourseTag.query.filter_by(text=t).filter_by(course_id=c.id).first()
            if tag is None:
                new_tags.append(CourseTag(text=t, course_id=c.id))
        db.session.add_all(new_tags)
        db.session.commit()
        flash('Edited course successfully', 'info')
        return redirect(url_for('admin.edit_course', id=c.id))
    context = {
        'course': c,
        'form': form
    }
    return render_template('admin/courses-edit.html', **context)

@admin.route('/course/create', methods=['POST'])
def create_course():
    if not current_user.is_authenticated:
        return redirect(url_for('admin.login'))
        
    form = AdminCreateCourseForm()
    filename_img = str(int(time.time() * 10)) + '.png'
    filename_vid = str(int(time.time() * 10)) + '.mp4'

    try:
        if not os.path.isdir('temp'):
            os.mkdir('temp')
        form.image.data.save(f"temp/{filename_img}")
        form.video.data.save(f"temp/{filename_vid}")
        video_length = float(VideoFileClip(f"{app.config.get('BASEDIR')}/temp/{filename_vid}").duration) / 60

        s3_client = boto3.client('s3', aws_access_key_id=app.config.get('AWS_ACCESS_KEY_ID'), aws_secret_access_key=app.config.get('AWS_SECRET_ACCESS_KEY'))
        # upload image
        s3_client.upload_fileobj(open(f'temp/{filename_img}', 'rb'), app.config.get('AWS_S3_BUCKET'), 'courses/thumbnails/' + filename_img, ExtraArgs={'ContentType': "image/png", 'ACL': 'public-read' })
        # upload video
        s3_client.upload_fileobj(open(f'temp/{filename_vid}', 'rb'), app.config.get('AWS_S3_BUCKET'), 'courses/videos/' + filename_vid, ExtraArgs={ 'ACL': 'public-read', 'ContentType': 'video/mp4' })

        course = Course()
        data = dict(name=form.name.data, icon=form.icon.data, video=filename_vid, skill_level_id=form.skill_level.data, video_length=video_length, video_thumbnail=filename_img, description=form.description.data, category_id=form.category.data)
        course.from_dict(data)
        course.save()

        # Remove all files in temp folder
        clear_temp_dir()
        flash('Course created successfully', 'success')
    except Exception as err:
        print(err)
        flash('There was an error', 'danger')
    return redirect(url_for('admin.courses'))

@admin.route('/course/delete')
def delete_course():
    if not current_user.is_authenticated:
        return redirect(url_for('admin.login'))
    try:
        _id = int(request.args.get('id'))
        course = Course.query.get(_id)
        course.delete()
        # TODO: find the image/video in the s3 buckets
        # TODO: delete them
        # s3_client = boto3.client('s3', aws_access_key_id=app.config.get('AWS_ACCESS_KEY_ID'), aws_secret_access_key=app.config.get('AWS_SECRET_ACCESS_KEY'))
        # print(help(s3_client.delete_object))
        # s3_client.delete_object(app.config('AWS_S3_BUCKET'), f'courses/thumbnails/{course.video_thumbnail}')
        # s3_client.delete_object(app.config('AWS_S3_BUCKET'), f'courses/videos/{course.video}')
        flash('Course deleted successfully', 'info')
        return redirect(url_for('admin.courses'))
    except ClientError as err:
        print(err)
        flash('There was a problem deleting the course', 'danger')
        return redirect(url_for('admin.courses'))

@admin.route('/course_categories', methods=['GET'])
def course_categories():
    form = AdminCreateCourseCategoryForm()
    if not current_user.is_authenticated:
        return redirect(url_for('admin.login'))
    return render_template('admin/course-categories.html', course_categories=[i.to_dict() for i in CourseCategory.query.all()], form=form)


@admin.route('/course_categories', methods=['POST'])
def create_course_category():
    if not current_user.is_authenticated:
        return redirect(url_for('admin.login'))

    form = AdminCreateCourseCategoryForm()
    filename_img = str(int(time.time() * 10)) + '.png'
    try:
        if not os.path.isdir('temp'):
            os.mkdir('temp')
            form.image.data.save(f"temp/{filename_img}")



            s3_client = boto3.client('s3', aws_access_key_id=app.config.get('AWS_ACCESS_KEY_ID'), aws_secret_access_key=app.config.get('AWS_SECRET_ACCESS_KEY'))
            # upload image
            s3_client.upload_fileobj(open(f'temp/{filename_img}', 'rb'), app.config.get('AWS_S3_BUCKET'), 'courses/categories/' + filename_img, ExtraArgs={'ContentType': "image/png", 'ACL': 'public-read' })

            c = CourseCategory()
            data = dict(name=form.name.data, icon=form.icon.data, image=filename_img)
            c.from_dict(data)
            c.save()

            # Remove all files in temp folder
            # TODO: Finish this part
            clear_temp_dir()
        flash('Course Category created successfully', 'success')
    except:
        flash('There was an error creating the Course Category', 'danger')
    return redirect(url_for('admin.course_categories'))


@admin.route('/course/category/edit', methods=['GET', 'POST'])
def edit_course_category():
    if not current_user.is_authenticated:
        return redirect(url_for('admin.login'))
    
    c = CourseCategory.query.get(request.args.get('id'))
    form = AdminEditCourseCategoryForm()
    form.name.data = c.name
    form.icon.data = c.icon

    if request.method == 'POST':
        # # Remove all files in temp folder
        
        if not os.path.isdir('temp'):
            os.mkdir('temp')

        if form.image_verify.data:
            form.image.data.save(f"temp/{form.image.data.filename}")
            
            # Connect to S3 client
            s3_client = boto3.client('s3', aws_access_key_id=app.config.get('AWS_ACCESS_KEY_ID'), aws_secret_access_key=app.config.get('AWS_SECRET_ACCESS_KEY'))

            # upload image
            s3_client.upload_fileobj(open(f'temp/{form.image.data.filename}', 'rb'), app.config.get('AWS_S3_BUCKET'), 'courses/categories/' + form.image.data.filename, ExtraArgs={'ContentType': "image/png", 'ACL': 'public-read' })

            c.name = request.form.get('name')
            c.icon = request.form.get('icon')
            c.image = form.image.data.filename
            os.remove(f'{app.config.get("BASEDIR")}/temp/{form.image.data.filename}')
        else:
            flash('You did not verify an image upload. Please make sure you meant to click the checkbox.', 'warning')
            c.name = request.form.get('name')
            c.icon = request.form.get('icon')
        db.session.commit()
        flash('Edited Course Category successfully', 'info')
        return redirect(url_for('admin.edit_course_category', id=c.id))
    context = {
        'c': c,
        'form': form
    }
    return render_template('admin/course-category-edit.html', **context)


@admin.route('/course/category/delete')
def delete_course_category():
    if not current_user.is_authenticated:
        return redirect(url_for('admin.login'))
    _id = int(request.args.get('id'))
    course_category = CourseCategory.query.get(_id)
    course_category.delete()
    flash('Course deleted successfully', 'info')
    return redirect(url_for('admin.course_categories'))

@admin.route('/users', methods=['GET', 'POST'])
def users():
    if not current_user.is_authenticated:
        return redirect(url_for('admin.login'))
    form = AdminUserForm()
    if current_user.is_admin and current_user.is_authenticated:
        form.role.choices = [(i.id, i.name) for i in Role.query.course_categorie_by(Role.name).all()]
    else:
        form.role.choices = [(i.id, i.name) for i in Role.query.course_categorie_by(Role.name).all() if i.name != 'Admin']
    # print(form.role.choices)
    if form.validate_on_submit():
        user = Account()
        data = {
            'email': form.email.data.lower(), 
            'first_name': form.first_name.data, 
            'last_name': form.last_name.data, 
            'password': form.email.data.lower()
        }
        user.from_dict(data)
        user.role_id = Role.query.get(form.role.data).id
        # print(Role.query.all())
        # print(Role.query.filter_by(name=form.role.data).first().id)
        if Role.query.get(form.role.data).name == 'Admin':
            user.is_admin = 1
        # print(data)
        user.set_password(user.password)
            # 'role_id': Role.query.filter_by(name=form.role.data.title()).first().id,
        user.create_account()
        flash('User created successfully', 'success')
        return redirect(url_for('admin.users'))
    if current_user.is_admin:
        users = [i for i in Account.query.all() if i != current_user]
    elif current_user.role.name == 'Owner':
        # print("owner")
        users = [i for i in Account.query.all() if i != current_user and not i.is_admin]
    else:
        users = [i for i in Account.query.all() if i != current_user and not i.is_admin]
        # print(users)
    # users = [i for i in Account.query.course_categorie_by(Account.last_name).all() if i != current_user]
    return render_template('admin/users.html', users=sorted(users, key=lambda x:x.role.rank), form=form)

@admin.route('/user/edit', methods=['GET', 'POST'])
def edit_user():
    if not current_user.is_authenticated:
        return redirect(url_for('admin.login'))
    u = Account.query.get(request.args.get('id'))
    form = AdminEditUserForm()
    form.role.choices = [(i.id, i.name) for i in Role.query.course_categorie_by(Role.name).all() if i.name != 'Admin']
    # print(u.role_id)

    if form.validate_on_submit():
        data = dict(first_name=form.first_name.data, last_name=form.last_name.data, email=form.email.data.lower())
        # print(form.role.data)
        u.role_id = form.role.data
        # print(u.role_id)
        u.is_admin = form.is_admin.data
        u.from_dict(data)
        db.session.commit()
        flash('Edited user successfully', 'info')
        return redirect(url_for('admin.users'))
    context = {
        'user': u,
        'form': form
    }
    return render_template('admin/users-edit.html', **context)

@admin.route('/user/delete')
def delete_account():
    if not current_user.is_authenticated:
        return redirect(url_for('admin.login'))
    _id = int(request.args.get('id'))
    user = Account.query.get(_id)
    user.delete_account()
    flash('User deleted successfully', 'info')
    return redirect(url_for('admin.users'))


@admin.route('/roles', methods=['GET'])
def roles():
    if not current_user.is_authenticated:
        return redirect(url_for('admin.login'))
    # print(current_user.is_admin)
    if current_user.is_admin:
        roles = Role.query.all()
    else:
        roles = [i for i in Role.query.all() if not i.name == 'Admin']
    return render_template('admin/roles.html', roles=sorted(roles, key=lambda x:x.rank))

@admin.route('/roles', methods=['POST'])
def create_role():
    if not current_user.is_authenticated:
        return redirect(url_for('admin.login'))
    if request.method == 'POST':
        role = Role()
        data = dict(name=request.form.get('name'))
        role.from_dict(data)
        role.create_role()
        flash('Role created successfully', 'success')
    return redirect(url_for('admin.roles'))

@admin.route('/roles/delete')
def delete_role():
    if not current_user.is_authenticated:
        return redirect(url_for('admin.login'))
    _id = int(request.args.get('id'))
    role = Role.query.get(_id)
    role.delete_role()
    flash('Course deleted successfully', 'info')
    return redirect(url_for('admin.roles'))
