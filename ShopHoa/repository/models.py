from ShopHoa import db,login_manager,app
from datetime import datetime
from werkzeug.security import generate_password_hash,check_password_hash
from flask_login import UserMixin
import json
from slugify import slugify
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from datetime import datetime

from flask_dance.consumer.storage.sqla import OAuthConsumerMixin,SQLAlchemyStorage
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(30) ,unique =False,nullable=False )
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(180), unique=False, nullable=False)
    profile = db.Column(db.String(180), unique=False, nullable=False, default='profile.jpg')

    def __repr__(self):
        return '<User %r>' % self.username

class Brand(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(30), unique=True, nullable=False)

class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(30), unique=True, nullable=False)

class Addproduct(db.Model):
    __searchable__ = ['name', 'discription']
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    price = db.Column(db.Numeric(10, 2), nullable=False)
    discount = db.Column(db.Integer, default=0)
    stock = db.Column(db.Integer, nullable=False)
    color = db.Column(db.Text, nullable=False)
    discription = db.Column(db.Text, nullable=False)
    pub_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    #comments = db.Column(db.Integer, default=0)
    #feature = db.Column(db.String, default=1, nullable=False)

    brand_id = db.Column(db.Integer, db.ForeignKey('brand.id'),nullable=False)
    brand = db.relationship('Brand',backref=db.backref('brands', lazy=True))

    category_id = db.Column(db.Integer, db.ForeignKey('category.id'), nullable=False)
    category = db.relationship('Category', backref=db.backref('posts', lazy=True))

    image_1 = db.Column(db.String(150), nullable=False, default='image.jpg')
    image_2 = db.Column(db.String(150), nullable=False, default='image.jpg')
    image_3 = db.Column(db.String(150), nullable=False, default='image.jpg')
    def __repr__(self):
        return '<Addproduct %r>' % self.name


@login_manager.user_loader
def user_loader(user_id):
    return Register.query.get(user_id)

class Register(db.Model,UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=False)
    #f_name = db.Column(db.String(50), unique=False)
    username = db.Column(db.String(80), unique=True)
    email = db.Column(db.String(120), unique=True)
    password = db.Column(db.String(180), unique=False)
    country = db.Column(db.String(50), unique=False)
    #state = db.Column(db.String(50), unique=False)
    city = db.Column(db.String(50), unique=False)
    contact = db.Column(db.String(50), unique=False)
    address = db.Column(db.String(50), unique=False)
    zipcode = db.Column(db.String(50), unique=False)
    profile =db.Column(db.String(200), unique=False, default ='profile.jpg' )
    date_created = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    def get_reset_token(self,expires_sec = 1800):
        s= Serializer(app.config['SECRET_KEY'], expires_sec)
        return  s.dumps({'user_id': self.id}).decode('utf-8')

    @staticmethod
    def verify_reset_token(token):
        s = Serializer(app.config['SECRET_KEY'])
        try:
            user_id = s.loads(token)['user_id']
        except:
            return None
        return Register.query.get(user_id)
    def __repr__(self):
        return '<Register %r>' % self.name

class JsonEcodedDict(db.TypeDecorator):
        impl = db.Text

        def process_bind_param(self, value, dialect):
            if value is None:
                return '{}'
            else:
                return json.dumps(value)

        def process_result_value(self, value, dialect):
            if value is None:
                return {}
            else:
                return json.loads(value)

class CustomerOrder(db.Model):
        id = db.Column(db.Integer, primary_key=True)
        invoice = db.Column(db.String(20), unique=True, nullable=False)
        status = db.Column(db.String(20), default='Pending', nullable=False)
        customer_id = db.Column(db.Integer, unique=False, nullable=False)
        date_created = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
        orders = db.Column(JsonEcodedDict)

        def __repr__(self):
            return '<CustomerOrder %r>' % self.invoice


class Post(db.Model):
    __searchable__ = ['title', 'body']
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), unique=True, nullable=False)
    #slug = db.Column(db.String(200), unique=True, nullable=False)
    body = db.Column(db.Text, nullable=False)
    category = db.Column(db.String(100), nullable=False)
    image = db.Column(db.String(150), nullable=False, default='no-image.jpg')
    #user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'), nullable=False)
    #author = db.relationship('User', backref=db.backref('posts',lazy=True, passive_deletes=True))
    views = db.Column(db.Integer,default=0)
    comments = db.Column(db.Integer,default=0)
    feature = db.Column(db.String, default=1, nullable=False)
    date_pub = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    def __repr__(self):
        return '<Post %r' % self.title

    @staticmethod
    def generate_slug(target, value, oldvalue, initiator):
        if value and (not target.slug or value != oldvalue):
            target.slug = slugify(value)
            db.event.listen(Post.title, 'set',Post.generate_slug, retval=False)


class Comments(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), unique=False, nullable=False)
    email = db.Column(db.String(200), unique=False, nullable=False)
    message = db.Column(db.Text, nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey('post.id', ondelete='CASCADE'), nullable=False)
    post = db.relationship('Post', backref=db.backref('posts',lazy=True, passive_deletes=True))
    feature = db.Column(db.Boolean, default=False, nullable=False)
    date_pub = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    def __repr__(self):
        return '<Post %r' % self.name

class Blog(db.Model):
    __searchable__ = ['title', 'body']
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), unique=True, nullable=False)
    slug = db.Column(db.String(200), unique=True, nullable=False)
    body = db.Column(db.Text, nullable=False)
    category = db.Column(db.String(100), nullable=False)
    image = db.Column(db.String(150), nullable=False, default='no-image.jpg')
    #user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'), nullable=False)
    #author = db.relationship('User', backref=db.backref('posts',lazy=True, passive_deletes=True))
    views = db.Column(db.Integer,default=0)
    comments = db.Column(db.Integer,default=0)
    feature = db.Column(db.String, default=1, nullable=False)
    date_pub = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

class OAuth(OAuthConsumerMixin, db.Model):
    user_id = db.Column(db.Integer, db.ForeignKey(Register.id))
    user = db.relationship(Register)




db.create_all()