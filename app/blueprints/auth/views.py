from flask_login import current_user, login_user, logout_user
from flask import redirect, render_template, url_for, flash, request
from .models import Account
from .import bp as auth
from .forms import AdminRegisterForm, AdminLoginForm

@auth.route('/', methods=['GET'])
def index():
    if not current_user.is_authenticated:
        return redirect(url_for('auth.login'))
    else:
        user = Account.query.get(current_user.id)
        if user is not None:
            logout_user()
            return redirect(url_for('auth.login'))
    return render_template('admin/index.html')

@auth.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    if request.args.get('is_authenticated') == 'false':
        # do something in there near future
        pass
    form = AdminLoginForm()
    if form.validate_on_submit():
        email = form.email.data.lower()
        password = form.password.data

        user = Account.query.filter_by(email=email).first()
        if user is None or not user.check_password(password):
            flash('You have entered either an incorrect email or password. Try again.', 'danger')
            return redirect(url_for('auth.login'))
        login_user(user, remember=form.remember_me.data)
        flash('You have logged in successfully', 'success')
        return redirect(url_for('main.home'))
    return render_template('auth/login.html', form=form)

@auth.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    form = AdminRegisterForm()
    if form.validate_on_submit():
        email = form.email.data.lower()
        password = form.password.data

        user = Account.query.filter_by(email=email).first()
        if user is not None:
            flash('That user already exists. Please try signing up with another email address.', 'warning')
            return redirect(url_for('auth.login'))
        u = Account()
        u.from_dict(dict(name=form.name.data, email=form.email.data, password=form.password.data))
        u.set_password(password)
        u.save()
        flash('You have registered successfully', 'success')
        return redirect(url_for('auth.login'))
    context = {
        'form': form
    }
    return render_template('auth/register.html', **context)

@auth.route('/logout')
def logout():
    if not current_user.is_authenticated:
        return redirect(url_for('auth.login'))
    logout_user()
    flash('You have logged out successfully', 'info')
    return redirect(url_for('auth.login'))
