from flask import current_app as app
from flask_login import current_user

@app.context_processor
def make_context():
    authenticated = None
    if current_user.is_anonymous:
        authenticated = False
    else:
        authenticated = True
    return dict(
        is_authenticated=authenticated, 
        subscription_basic=app.config.get('SUBSCRIPTION_BASIC'), 
        stripe_pub_key=app.config.get('STRIPE_PUB_KEY'), 
        stripe_test_key=app.config.get('STRIPE_SECRET_KEY'),
        home_url=app.config.get('HOME_URL')
        )