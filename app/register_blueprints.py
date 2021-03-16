from flask import current_app as app
from app.blueprints.main import bp as main
from app.blueprints.courses import bp as courses
from app.blueprints.auth import bp as auth
from app.blueprints.shop import bp as shop

app.register_blueprint(main)
app.register_blueprint(courses)
app.register_blueprint(auth)
app.register_blueprint(shop)