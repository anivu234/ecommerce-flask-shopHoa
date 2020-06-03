from wtforms import Form, BooleanField, StringField, PasswordField, validators,IntegerField,TextAreaField,SubmitField,ValidationError
from flask_wtf.file import FileAllowed,FileField,FileRequired
from wtforms.validators import DataRequired,ValidationError,Email,EqualTo
from ShopHoa.repository.models import *
from flask_wtf import FlaskForm,RecaptchaField
from flask_login import current_user


class RegistrationForm(Form):
    name =StringField('Name', [validators.Length(min=4, max=25)])
    username = StringField('Username', [validators.Length(min=4, max=25)])
    email = StringField('Email Address', [validators.Length(min=6, max=35),validators.Email()])
    password = PasswordField('New Password', [validators.DataRequired(),validators.EqualTo('confirm', message='Passwords must match')])

    confirm = PasswordField('Repeat Password')



class LoginForm(Form):
    email = StringField("Email address", [validators.Length(min =6,max=35),validators.Email()])
    password = PasswordField("Passowrd", [validators.DataRequired()])
    submit = SubmitField('Login')

class Addproducts(Form):
    name = StringField('Name',[validators.DataRequired()])
    price = IntegerField('Price',[validators.DataRequired()])
    discount = IntegerField('Discount',[validators.DataRequired()])
    stock = IntegerField('Stock',[validators.DataRequired()])
    discription = TextAreaField('Discription',[validators.DataRequired()])
    color = TextAreaField('Colors',[validators.DataRequired()])

    image_1= FileField('Image1', validators=[FileRequired(), FileAllowed(['jpg','png','gif','jpeg'],'Images only!')])
    image_2= FileField('Image2', validators=[FileRequired(), FileAllowed(['jpg','png','gif','jpeg'],'Images only!')])
    image_3= FileField('Image3', validators=[FileRequired(), FileAllowed(['jpg','png','gif','jpeg'],'Images only!')])


class CustomerRegisterForm(FlaskForm):
    name = StringField('Name: ')
    username = StringField('Username: ', [validators.DataRequired()])
    email = StringField('Email: ', [validators.Email(), validators.DataRequired()])
    password = PasswordField('Password: ', [validators.DataRequired(),validators.EqualTo('confirm', message=' Both password must match! ')])
    confirm = PasswordField('Repeat Password: ', [validators.DataRequired()])
    country = StringField('Country: ', [validators.DataRequired()])
    city = StringField('City: ', [validators.DataRequired()])
    contact = StringField('Contact: ', [validators.DataRequired()])
    address = StringField('Address: ', [validators.DataRequired()])
    zipcode = StringField('Zip code: ', [validators.DataRequired()])
    recaptcha = RecaptchaField()
    profile = FileField('Profile', validators=[FileAllowed(['jpg', 'png', 'jpeg', 'gif'], 'Image only please')])
    submit = SubmitField('Register')

    def validate_username(self, username):
            user = Register.query.filter_by(username=username.data).first()
            if user:
                raise ValidationError("This username is already in use!")

    def validate_email(self, email):
            user = Register.query.filter_by(email=email.data).first()
            if user:
                raise ValidationError("This email address is already in use!")


class CustomerLoginFrom(FlaskForm):
    email = StringField('Email: ', [validators.Email(), validators.DataRequired()])
    password = PasswordField('Password: ', [validators.DataRequired()])
    recaptcha = RecaptchaField()

class CustomerUpdateForm(FlaskForm):
    name = StringField('Name: ')
    username = StringField('Username: ', [validators.DataRequired()])
    email = StringField('Email: ', [validators.Email(), validators.DataRequired()])

    country = StringField('Country: ', [validators.DataRequired()])
    city = StringField('City: ', [validators.DataRequired()])
    contact = StringField('Contact: ', [validators.DataRequired()])
    address = StringField('Address: ', [validators.DataRequired()])
    zipcode = StringField('Zip code: ', [validators.DataRequired()])

    profile = FileField('Profile', validators=[FileAllowed(['jpg', 'png', 'jpeg', 'gif'], 'Image only please')])
    submit = SubmitField('Update')

    def validate_username(self, username):
        if username.data != current_user.username:
            user = Register.query.filter_by(username= username.data).first()
            if user:
                raise ValidationError("This username is already in use!")

    def validate_email(self, email):
        if email.data != current_user.email:
                user =Register.query.filter_by(email=email.data).first()
                if user:
                    raise ValidationError("This email address is already in use!")

class RequestResetForm(FlaskForm):
    email = StringField('Email: ', [validators.Email(), validators.DataRequired()])
    submit = SubmitField('Request Password Reset')

    def validate_email(self, email):
        user =Register.query.filter_by(email=email.data).first()
        if user is None:
            raise ValidationError("There is no account with that email.You must register first..")

class ResetPasswordForm(FlaskForm):
    password = PasswordField('Password: ', [validators.DataRequired(),validators.EqualTo('confirm', message=' Both password must match! ')])
    confirm = PasswordField('Repeat Password: ', [validators.DataRequired()])
    submit = SubmitField('  Reset Password')

class ContactForm(FlaskForm):
    name = StringField('Name:', validators=[DataRequired('Please enter your name.')])
    email = StringField('E-mail:', validators=[DataRequired('Please enter your email address.'),validators.Email("Please enter your email address.")])
    subject = StringField('Subject:', validators=[DataRequired('Please enter a subject.')])
    phone = StringField('Phone: ', [validators.DataRequired('Please enter a phone')])
    message = TextAreaField('Message:', validators=[DataRequired('Please enter a message.')])
    submit = SubmitField("Send")

class PostForm(Form):
    title = StringField('Title',[validators.DataRequired()])
    content = TextAreaField('Content', [validators.DataRequired()])
    photo = FileField()