from .import bp as admin
from flask import render_template, redirect, url_for, request, flash, session, current_app
from app.models import Hair, Customer, Coupon, HairCategory, Pattern, Account, Role, HairTip, Order
from .forms import AdminUserForm, AdminLoginForm, AdminEditUserForm, AdminEditUserForm, AdminCreateProductForm, AdminResetPasswordRequestForm, AdminResetPasswordForm, AdminCreatePatternForm, AdminEditPatternForm, AdminEditProductForm, AdminCreateHairTipForm, AdminEditHairTipForm
from flask_login import current_user, login_user, logout_user
from app import db
from .email import send_password_reset_email
import requests
from datetime import datetime as dt
from cloudinary.uploader import upload

@admin.route('/', methods=['GET'])
def index():
    if not current_user.is_authenticated:
        return redirect(url_for('admin.login'))
    else:
        customer = Customer.query.get(current_user.id)
        if customer is not None:
            logout_user()
            return redirect(url_for('admin.login'))
    return render_template('admin/index.html')

@admin.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('admin.index'))
    form = AdminLoginForm()
    if form.validate_on_submit():
        email = form.email.data.lower()
        password = form.password.data

        user = Account.query.filter_by(email=email).first()
        if user is None or not user.check_password(password):
            flash('You have entered either an incorrect email or password. Try again.', 'danger')
            return redirect(url_for('admin.login'))
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

@admin.route('/coupons', methods=['GET'])
def coupons():
    if not current_user.is_authenticated:
        return redirect(url_for('admin.login'))
    return render_template('admin/coupons.html', coupons=Coupon.query.all())

@admin.route('/coupons', methods=['POST'])
def create_coupon():
    if not current_user.is_authenticated:
        return redirect(url_for('admin.login'))
    if request.method == 'POST':
        coupon = Coupon()
        data = dict(text=request.form.get('coupon_code'), discount=request.form.get('discount'))
        coupon.from_dict(data)
        coupon.create_coupon()
        flash('Coupon created successfully', 'success')
    return redirect(url_for('admin.coupons'))

@admin.route('/coupons/delete')
def delete_coupon():
    if not current_user.is_authenticated:
        return redirect(url_for('admin.login'))
    _id = int(request.args.get('id'))
    coupon = Coupon.query.get(_id)
    coupon.delete_coupon()
    flash('Coupon deleted successfully', 'info')
    return redirect(url_for('admin.coupons'))

@admin.route('/users', methods=['GET', 'POST'])
def users():
    if not current_user.is_authenticated:
        return redirect(url_for('admin.login'))
    form = AdminUserForm()
    if current_user.is_admin and current_user.is_authenticated:
        form.role.choices = [(i.id, i.name) for i in Role.query.order_by(Role.name).all()]
    else:
        form.role.choices = [(i.id, i.name) for i in Role.query.order_by(Role.name).all() if i.name != 'Admin']
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
    # users = [i for i in Account.query.order_by(Account.last_name).all() if i != current_user]
    return render_template('admin/users.html', users=sorted(users, key=lambda x:x.role.rank), form=form)

@admin.route('/user/edit', methods=['GET', 'POST'])
def edit_user():
    if not current_user.is_authenticated:
        return redirect(url_for('admin.login'))
    u = Account.query.get(request.args.get('id'))
    form = AdminEditUserForm()
    form.role.choices = [(i.id, i.name) for i in Role.query.order_by(Role.name).all() if i.name != 'Admin']
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
    flash('Coupon deleted successfully', 'info')
    return redirect(url_for('admin.roles'))


@admin.route('/hair/products', methods=['GET', 'POST'])
def hair_products():
    if not current_user.is_authenticated:
        return redirect(url_for('admin.login'))
    form = AdminCreateProductForm()
    form.pattern.choices = [(i.id, i.name) for i in Pattern.query.order_by(Pattern.name).all()]
    form.category.choices = [(i.id, i.name) for i in HairCategory.query.order_by(HairCategory.name).all()]

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
    return render_template('admin/hair/products.html', products=Hair.query.order_by(Hair.pattern).all(), form=form)

@admin.route('/hair/product/edit', methods=['GET', 'POST'])
def edit_hair_product():
    if not current_user.is_authenticated:
        return redirect(url_for('admin.login'))
    p = Hair.query.get(request.args.get('id'))
    form = AdminEditProductForm()
    form.pattern.choices = [(i.id, i.name) for i in Pattern.query.order_by(Pattern.name).all()]
    form.category.choices = [(i.id, i.name) for i in HairCategory.query.order_by(HairCategory.name).all()]

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
    form.name.choices = [(i.id, i.name) for i in Pattern.query.order_by(Pattern.name).all()]
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


@admin.route('/orders', methods=['GET'])
def orders():
    if not current_user.is_authenticated:
        return redirect(url_for('admin.login'))
    return render_template('admin/orders.html', orders=[i.to_dict() for i in Order.query.all()])


@admin.route('/orders', methods=['POST'])
def create_order():
    pass
    # if not current_user.is_authenticated:
    #     return redirect(url_for('admin.login'))
    # if request.method == 'POST':
    #     order = Coupon()
    #     data = dict(customer_id=request.form.get('order_code'),
    #                 cart_id=request.form.get('discount'),
    #                 product_id=)
    #     order.from_dict(data)
    #     order.create_order()
    #     flash('Coupon created successfully', 'success')
    # return redirect(url_for('admin.orders'))


@admin.route('/orders/delete')
def delete_order():
    if not current_user.is_authenticated:
        return redirect(url_for('admin.login'))
    _id = int(request.args.get('id'))
    order = Coupon.query.get(_id)
    order.delete_order()
    flash('Coupon deleted successfully', 'info')
    return redirect(url_for('admin.orders'))