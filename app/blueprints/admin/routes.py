from .import bp as admin
from flask import render_template, redirect, url_for, request, flash, session, current_app
from app.blueprints.courses.models import Course, CourseCategory, CourseTag
from app.blueprints.auth.models import Account
from .forms import AdminEditCourseCategoryForm, AdminLoginForm, AdminEditUserForm, AdminCreateCourseForm, AdminResetPasswordRequestForm, AdminResetPasswordForm, AdminEditCourseForm
from flask_login import current_user, login_user, logout_user
from app import db
import requests, stripe
from datetime import datetime as dt

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

@admin.route('/courses', methods=['GET'])
def courses():
    if not current_user.is_authenticated:
        return redirect(url_for('admin.login'))
    form = AdminCreateCourseForm()
    form.category.choices = [(i.id, i.name) for i in CourseCategory.query.order_by(CourseCategory.name).all()]
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
        form.description.data = c.description
        form.category.data = c.category_id
        form.tags.data = ', '.join([i.text for i in CourseTag.query.filter_by(course_id=c.id).all()])

    if request.method == 'POST':
        form = AdminEditCourseForm()
        
        data = dict(name=form.name.data, icon=form.icon.data, video=form.video.data, description=form.description.data, video_thumbnail=form.video_thumbnail.data, category_id=form.category.data)
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

@admin.route('/courses', methods=['POST'])
def create_course():
    pass
    # if not current_user.is_authenticated:
    #     return redirect(url_for('admin.login'))
    # if request.method == 'POST':
    #     course = Course()
    #     data = dict(text=request.form.get('course_code'), discount=request.form.get('discount'))
    #     course.from_dict(data)
    #     db.session.commit()
    #     flash('Course created successfully', 'success')
    # return redirect(url_for('admin.courses'))

@admin.route('/courses/delete')
def delete_course():
    if not current_user.is_authenticated:
        return redirect(url_for('admin.login'))
    _id = int(request.args.get('id'))
    course = Course.query.get(_id)
    course.delete_course()
    flash('Course deleted successfully', 'info')
    return redirect(url_for('admin.courses'))

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

# @admin.route('/users', methods=['POST'])
# def create_user():
#     if request.method == 'POST':
#         user = Account()
#         data = {
#             'email': request.form.get('email'), 
#             'password': request.form.get('email')
#         }
#         user.from_dict(data)
#         user.role_id = Role.query.filter_by(name=request.form.get('role').title()).first().id
#         print(Role.query.all())
#         print(Role.query.filter_by(name=request.form.get('role')).first().id)
#         if request.form.get('is_admin') is not None:
#             user.is_admin = request.form.get('is_admin')
#         user.set_password_hash(user.password)
#             # 'role_id': Role.query.filter_by(name=request.form.get('role').title()).first().id,
#         user.create_user()
#         flash('User created successfully', 'success')
#     return redirect(url_for('admin.users'))

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


@admin.route('/hair/products', methods=['GET', 'POST'])
def hair_products():
    if not current_user.is_authenticated:
        return redirect(url_for('admin.login'))
    form = AdminCreateCourseForm()
    form.pattern.choices = [(i.id, i.name) for i in Pattern.query.course_categorie_by(Pattern.name).all()]
    form.category.choices = [(i.id, i.name) for i in HairCategory.query.course_categorie_by(HairCategory.name).all()]

    if form.validate_on_submit():
        product = Hair()
        data = {
            'pattern': Pattern.query.get(form.pattern.data).name, 
            'length': form.length.data,
            'price': form.price.data, 
            'category_id': HairCategory.query.get(int(form.category.data)).name,
        }
        product.from_dict(data)
        product.pattern_id = Pattern.query.get(form.pattern.data).id
        product.category_id = HairCategory.query.get(form.category.data).id
        # product.bundle_length = form.bundle_length.data or ''
        product.create_hair_product()
        flash('Hair Product created successfully', 'success')
        return redirect(url_for('admin.hair_products'))
    return render_template('admin/hair/products.html', products=Hair.query.course_categorie_by(Hair.pattern).all(), form=form)

@admin.route('/hair/product/edit', methods=['GET', 'POST'])
def edit_hair_product():
    if not current_user.is_authenticated:
        return redirect(url_for('admin.login'))
    p = Hair.query.get(request.args.get('id'))
    form = AdminEditCourseForm()
    form.pattern.choices = [(i.id, i.name) for i in Pattern.query.course_categorie_by(Pattern.name).all()]
    form.category.choices = [(i.id, i.name) for i in HairCategory.query.course_categorie_by(HairCategory.name).all()]

    if form.validate_on_submit():
        data = {
            'pattern': Pattern.query.get(form.pattern.data).name, 
            'length': form.length.data,
            'price': form.price.data, 
            'category_id': HairCategory.query.get(int(form.category.data)).name,
        }
        p.from_dict(data)
        p.pattern_id = Pattern.query.get(form.pattern.data).id
        p.category_id = HairCategory.query.get(form.category.data).id
        db.session.commit()
        flash('Edited product successfully', 'info')
        return redirect(url_for('admin.hair_products'))
    context = {
        'product': p,
        'form': form
    }
    return render_template('admin/hair/products-edit.html', **context)

@admin.route('/hair/product/delete')
def delete_hair_product():
    if not current_user.is_authenticated:
        return redirect(url_for('admin.login'))
    _id = int(request.args.get('id'))
    product = Hair.query.get(_id)
    product.delete_hair_product()
    flash('User deleted successfully', 'info')
    return redirect(url_for('admin.hair_products'))

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


####################################
# PATTERNS
####################################
@admin.route('hair/patterns', methods=['GET', 'POST'])
def hair_patterns():
    if not current_user.is_authenticated:
        return redirect(url_for('admin.login'))
    form = AdminCreatePatternForm()
    if form.validate_on_submit():
        file = request.files.get('image')
        result = upload(file)
        pattern = Pattern()
        data = {
            'name': form.name.data.title(), 
            'image': result['url'],
        }
        pattern.from_dict(data)
        pattern.create_hair_pattern()
        flash('Pattern created successfully', 'success')
        return redirect(url_for('admin.hair_patterns'))
    return render_template('admin/hair/patterns.html', patterns=Pattern.query.all(), form=form)

@admin.route('/hair/pattern/edit', methods=['GET', 'POST'])
def edit_hair_pattern():
    if not current_user.is_authenticated:
        return redirect(url_for('admin.login'))
    p = Pattern.query.get(request.args.get('id'))
    form = AdminEditPatternForm()
    form.name.choices = [(i.id, i.name) for i in Pattern.query.course_categorie_by(Pattern.name).all()]
    if form.validate_on_submit():
        p = Pattern.query.get(form.name.data)
        file = request.files.get('image')
        result = upload(file)
        data = {
            'name': Pattern.query.get(form.name.data).name,
            'image': result['url'], 
        }
        p.from_dict(data)
        db.session.commit()
        flash('Edited pattern successfully', 'info')
        return redirect(url_for('admin.hair_patterns'))
    context = {
        'pattern': p,
        'form': form
    }
    return render_template('admin/hair/patterns-edit.html', **context)

@admin.route('/hair/pattern/delete')
def delete_hair_pattern():
    if not current_user.is_authenticated:
        return redirect(url_for('admin.login'))
    _id = int(request.args.get('id'))
    pattern = Pattern.query.get(_id)
    pattern.delete_hair_pattern()
    flash('Pattern deleted successfully', 'info')
    return redirect(url_for('admin.hair_patterns'))


####################################
# HAIR TIPS
####################################
@admin.route('hair/tips', methods=['GET', 'POST'])
def hair_tips():
    if not current_user.is_authenticated:
        return redirect(url_for('admin.login'))
    form = AdminCreateHairTipForm()
    if form.validate_on_submit():
        ht = HairTip()
        data = {
            'description': form.description.data, 
        }
        ht.from_dict(data)
        ht.create_tip()
        flash('Hair Tip created successfully', 'success')
        return redirect(url_for('admin.hair_tips'))
    return render_template('admin/hair/tips.html', tips=HairTip.query.all(), form=form)

@admin.route('/hair/tip/edit', methods=['GET', 'POST'])
def edit_hair_tip():
    if not current_user.is_authenticated:
        return redirect(url_for('admin.login'))
    ht = HairTip.query.get(request.args.get('id'))
    form = AdminEditHairTipForm()
    if form.validate_on_submit():
        data = {
            'description': form.description.data,
        }
        ht.from_dict(data)
        db.session.commit()
        flash('Hair tip updated successfully', 'info')
        return redirect(url_for('admin.hair_tips'))
    context = {
        'tip': ht,
        'form': form
    }
    return render_template('admin/hair/tips-edit.html', **context)

@admin.route('/hair/tip/delete')
def delete_hair_tip():
    if not current_user.is_authenticated:
        return redirect(url_for('admin.login'))
    _id = int(request.args.get('id'))
    ht = HairTip.query.get(_id)
    ht.delete_hair_tip()
    flash('Hair tip deleted successfully', 'info')
    return redirect(url_for('admin.hair_tips'))


@admin.route('/course_categories', methods=['GET'])
def course_categories():
    if not current_user.is_authenticated:
        return redirect(url_for('admin.login'))
    return render_template('admin/course-categories.html', course_categories=[i.to_dict() for i in CourseCategory.query.all()])


@admin.route('/course_categories', methods=['POST'])
def create_course_category():
    if not current_user.is_authenticated:
        return redirect(url_for('admin.login'))
    if request.method == 'POST':
        c = CourseCategory()
        data = dict(name=request.form.get('name'),
                    icon=request.form.get('icon'))
        c.from_dict(data)
        c.save()
        flash('Course created successfully', 'success')
    return redirect(url_for('admin.course_categories'))


@admin.route('/course/category/edit', methods=['GET', 'POST'])
def edit_course_category():
    pass
    if not current_user.is_authenticated:
        return redirect(url_for('admin.login'))
    c = CourseCategory.query.get(request.args.get('id'))
    form = AdminEditCourseCategoryForm()
    if request.method == 'POST':
        form = AdminEditCourseCategoryForm()
        data = dict(name=form.name.data, icon=form.icon.data)
        c.from_dict(data)
        db.session.commit()
        flash('Edited course category successfully', 'info')
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
