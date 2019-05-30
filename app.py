
from flask import Flask, g
import models
from flask_cors import CORS
import config
from flask_login import LoginManager, current_user
from resources.users import users_api
from resources.phrases import phrases_api


app = Flask(__name__)
app.secret_key = config.SECRET_KEY

login_manager = LoginManager()
login_manager.init_app(app)


@login_manager.user_loader
def load_user(userid):
    try:
        return models.User.get(models.User.id == userid)
    except models.DoesNotExist:
        return None


# app.use(dogControllr, '/api/v1')
# url prefix star

CORS(users_api, origins=["http://localhost:3000"], supports_credentials=True)
CORS(phrases_api, origins=["http://localhost:3000"], supports_credentials=True)
app.register_blueprint(users_api, url_prefix='/users')
app.register_blueprint(phrases_api, url_prefix='/phrases')

# @app.before_request
# def before_request():
#     g.db = models.DATABASE
#     g.db.connect()
@app.before_request
def before_request():
    """Connect to the database before each request"""
    g.db = models.DATABASE
    g.db.connect()
   #and current_user to the global object so you can access it anywhere
    g.user = current_user

# anywhere you can grab the full user object by running 



@app.after_request
def after_request(response):
    g.db.close()
    return response


@app.route('/')
def index():
    return 'HIT'


if __name__ == '__main__':
    models.initialize()
    app.run(debug=config.DEBUG, port=config.PORT)
