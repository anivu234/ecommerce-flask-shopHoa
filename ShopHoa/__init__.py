from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_uploads import IMAGES, UploadSet, configure_uploads, patch_request_class
import os
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_mail import Mail
from flask_msearch import Search
import feedparser
from flask_dance.contrib.github import make_github_blueprint,github
from pusher import pusher
import simplejson
from flask_msearch import Search
from flask_dance.contrib.twitter import make_twitter_blueprint,twitter
from flask_dance.contrib.github import make_github_blueprint,github



basedir = os.path.abspath(os.path.dirname(__file__))
app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///shophoa.db'
app.config['SECRET_KEY'] = 'ray_qMkwVJmD2peu-oT8x_UK5wZnUIYldPVFK15VJPw='
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True

#search
#Twtich
twitter_blueprint = make_twitter_blueprint(api_key='', api_secret='')
github_blueprint = make_github_blueprint(client_id='32aae7c2c68f56a8505c',client_secret='5866ae915c7d42402d1ae082a10692c7b3a5abdd')
app.register_blueprint(github_blueprint, url_prefix="/github_login")
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'


RSS_feeds = {'BBC': 'http://feeds.bbci.co.uk/news/rss.xml',
             'CNN': 'http://rss.cnn.com/rss/edition.rss'}



app.config['RECAPTCHA_PUBLIC_KEY']='6LesHP0UAAAAAKoO0u1nM487Lvole3CeXEse5qW3'
app.config['RECAPTCHA_PRIVATE_KEY']='6LesHP0UAAAAACitGsdjLeQvR8my_gX5-TuPsDnu'




app.config['UPLOADED_PHOTOS_DEST'] = os.path.join(basedir, 'static/images')
photos = UploadSet('photos', IMAGES)
configure_uploads(app, photos)
patch_request_class(app)


db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
search = Search()
search.init_app(app)



migrate = Migrate(app, db)
with app.app_context():
    if db.engine.url.drivername == "sqlite":
        migrate.init_app(app, db, render_as_batch=True)
    else:
        migrate.init_app(app, db)


login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'customerLogin'
login_manager.needs_refresh_message_category= 'danger'
login_manager.login_message = u"Please login first"

app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'a1.kungfupanda@gmail.com'
app.config['MAIL_PASSWORD'] = 'dikudwlqcuwyfmjv'
mail =Mail(app)





from ShopHoa import app_index
from ShopHoa import app_admin
from ShopHoa import app_cart
