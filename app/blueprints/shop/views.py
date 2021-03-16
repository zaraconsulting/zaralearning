from flask import redirect, render_template, request, jsonify, url_for, current_app as app
import stripe
from .import bp as shop
from flask_login import current_user
from app.blueprints.auth.models import Account
from app import db

stripe.api_key = app.config.get('STRIPE_SECRET_KEY')

@shop.route('/create-customer-portal-session', methods=['POST'])
def customer_portal():
    # Authenticate your user.
    user = Account.query.get(current_user.id)
    if not user.is_customer:
        new_customer = stripe.Customer.create(email=user.email, name=user.name)
        user.customer_id = new_customer.id
        user.is_customer = True
        db.session.commit()
    else:
        customer = stripe.Customer.retrieve(user.customer_id)
        session = stripe.billing_portal.Session.create(
            customer=customer.id,
            return_url='http://localhost:5000/',
        )
    return redirect(session.url)

@shop.route('/subscribe', methods=['POST'])
def subscribe():
    data = request.json
    
    user = Account.query.get(current_user.id)
    if not user.is_customer:
        customer = stripe.Customer.create(email=user.email, name=user.name)
        user.customer_id = customer.id
        user.is_customer = True
        db.session.commit()
    else:
        customer = stripe.Customer.retrieve(user.customer_id)
    try:
        checkout_session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            customer=customer.id,
            line_items=[
                {
                    "price": data['priceId'],
                    # For metered billing, do not pass quantity
                    "quantity": 1
                }
            ],
            mode='subscription',
            success_url='http://127.0.0.1:5000?session_id={CHECKOUT_SESSION_ID}',
            cancel_url='http://127.0.0.1:5000?success',
        )
        return jsonify({'sessionId': checkout_session.id})
    except Exception as e:
        return jsonify(error=str(e)), 403
    return redirect(url_for('main.home'))