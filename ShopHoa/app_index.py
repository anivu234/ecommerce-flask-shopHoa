from flask import render_template, request, Markup, session, flash, redirect, url_for, g,jsonify,make_response
from ShopHoa import app,db,photos,bcrypt,login_manager,mail,RSS_feeds,search
from ShopHoa.repository.form import *
from ShopHoa.repository.models import *
from flask_login import current_user,login_user,logout_user,login_required
from flask_mail import Message
from flask_dance.contrib.github import  github
import random
import secrets
import os
from PIL import Image
from pusher import pusher
import stripe
import feedparser
import token
import json
import pdfkit



publishable_key ='pk_test_n6sYRcKl3gZJYiqLbLrHDNH300dOljH8aT'
stripe.api_key = 'sk_test_27WETnc31oqdy89oqqQKgaHn00lbgzaK8e'

@app.route('/payment',methods=["POST"])
@login_required
def payment():
    invoice = request.form.get('invoice')
    amount = request.form.get('amount')
    customer = stripe.Customer.create(
        email=request.form['stripeEmail'],
        source=request.form['stripeToken'],
    )
    charge = stripe.Charge.create(
        customer=customer.id,
        description='ShopHoa',
        amount=amount,
        currency='usd',
    )
    orders = CustomerOrder.query.filter_by(customer_id=current_user.id, invoice=invoice).order_by(CustomerOrder.id.desc()).first()
    orders.status = 'Paid'
    db.session.commit()
    return redirect(url_for('thanks'))

@app.route('/thanks')
def thanks():
    return render_template('thanks.html')


@app.route("/", methods=["GET", "POST"])
def index():
    posts = Post.query.order_by(Post.id.desc()).all()
    shops = Addproduct.query.filter(Addproduct.stock > 0).order_by(Addproduct.id.desc())
    products = Addproduct.query.filter(Addproduct.stock > 0).order_by(Addproduct.id.desc())
    random_shops = random.sample(list(products),6)
    random_post = random.sample(list(posts), 2)
    print(random_shops,random_post)
    return render_template("index.html", shops =shops, products = random_shops,posts =random_post)

@app.route("/sanpham", methods=["GET", "POST"])
def SanPham():

    page =request.args.get('page',1, type =int)
    products = Addproduct.query.filter(Addproduct.stock > 0).order_by(Addproduct.id.desc()).paginate(page=page,per_page=8)
    barnds =Brand.query.join(Addproduct,(Brand.id == Addproduct.brand_id)).all()
    categories = Category.query.join(Addproduct, (Category.id == Addproduct.category_id)).all()
    posts = Post.query.order_by(Post.id.desc()).all()
    random_post = random.sample(list(posts), 2)
    print(random_post)
    return render_template("SanPham.html",products =products,barnds = barnds,categories =categories,posts= random_post)

@app.route("/brand/<int:id>")
def get_brand(id):
    get_b = Brand.query.filter_by(id=id).first_or_404()
    page = request.args.get('page',1, type=int)
    brand =Addproduct.query.filter_by(brand =get_b).paginate(page = page,per_page=6)
    barnds = Brand.query.join(Addproduct, (Brand.id == Addproduct.brand_id)).all()
    categories = Category.query.join(Addproduct, (Category.id == Addproduct.category_id)).all()
    posts = Post.query.order_by(Post.id.desc()).all()
    random_post = random.sample(list(posts), 2)
    print(random_post)
    return render_template("SanPham.html", brand = brand,barnds =barnds,categories =categories,get_b =get_b,posts= random_post)

@app.route("/categories/<int:id>")
def get_category(id):
    page = request.args.get('page',1, type=int)
    get_cat =Category.query.filter_by(id=id).first_or_404()
    get_cat_prod =Addproduct.query.filter_by(category =get_cat).paginate(page = page,per_page=6)
    barnds = Brand.query.join(Addproduct, (Brand.id == Addproduct.brand_id)).all()
    categories = Category.query.join(Addproduct, (Category.id == Addproduct.category_id)).all()
    posts = Post.query.order_by(Post.id.desc()).all()
    random_post = random.sample(list(posts), 2)
    print(random_post)
    return render_template("SanPham.html",get_cat_prod =get_cat_prod, categories = categories, barnds =barnds,get_cat = get_cat,posts= random_post)

@app.route("/sanpham/<int:id>")
def single_page(id):
    posts = Post.query.order_by(Post.id.desc()).all()
    random_post = random.sample(list(posts), 2)
    print(random_post)
    product = Addproduct.query.get_or_404(id)
    barnds = Brand.query.join(Addproduct, (Brand.id == Addproduct.brand_id)).all()
    categories = Category.query.join(Addproduct, (Category.id == Addproduct.category_id)).all()
    post = Post.query.get_or_404(id)
    comment = Comments.query.filter_by(post_id=product.id).filter_by(feature=True).all()
    post.views = post.views + 1
    db.session.commit()
    Thanks = ""
    if request.method == "POST":
        post_id = product.id
        name = request.form.get('name')
        email = request.form.get('email')
        message = request.form.get('message')
        comment = Comments(name=name, email=email, message=message, post_id=post_id)
        db.session.add(comment)
        product.comments = product.comments + 1
        db.session.commit()
        flash('Your comment has been submited  submitted will be published after aproval of admin', 'success')
        return redirect(request.url)
    return render_template("single_page.html",product = product,categories = categories, barnds =barnds, post=post, comment=comment, Thanks=Thanks,posts= random_post)

@app.route('/register',methods= ['GET', 'POST'])
def customer_register():
    posts = Post.query.order_by(Post.id.desc()).all()
    random_post = random.sample(list(posts), 2)
    print(random_post)
    form = CustomerRegisterForm()
    if form.validate_on_submit():
        hash_password = bcrypt.generate_password_hash(form.password.data)
        register = Register(name=form.name.data, username=form.username.data, email=form.email.data,
                            password=hash_password, country=form.country.data,
                            city=form.city.data, address=form.address.data,contact= form.contact.data,
                            zipcode=form.zipcode.data)
        db.session.add(register)
        flash(f'Welcome {form.name.data} Thank you for registering', 'success')
        db.session.commit()
        return redirect(url_for('customerLogin'))
    return render_template('register.html', form=form,posts= posts)

@app.route('/login',methods= ['GET', 'POST'])
def customerLogin():
    posts = Post.query.order_by(Post.id.desc()).all()
    random_post = random.sample(list(posts), 2)
    print(random_post)
    form = CustomerLoginFrom()
    if form.validate_on_submit():
        user = Register.query.filter_by(email =form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user)
            flash('You are login now', 'success')
            next= request.args.get('next')
            return redirect(next or url_for('index'))
        flash('Incorrect email and password', 'danger')
        return  redirect(url_for('customerLogin'))
    return render_template('login.html',title = 'Sign in', form = form,posts= random_post)

@app.route('/logout')
def customer_logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/about')
def about():

 return render_template('about.html')

def save_picture(form_picture):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.sqlitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(app.root_path, 'static/profile_pics', picture_fn)

    output_size = (125,125)
    i = Image.open(form_picture)
    i.thumbnail(output_size)
    i.save(picture_path)

    return picture_fn

@app.route("/account",methods= ['GET', 'POST'])
@login_required
def account():
    form = CustomerUpdateForm()
    if form.validate_on_submit():
        if form.profile.data:
            picture_file = save_picture(form.profile.data)
            current_user.profile = picture_file
        current_user.username = form.username.data
        current_user.email = form.email.data
        db.session.commit()
        flash(f'you account has been updated', 'success' )
        return redirect(url_for('account'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email
    profile = url_for('static', filename='profile_pics/' + current_user.profile)
    return render_template('profile.html', title='Sign in', profile = profile, form = form)


def send_reset_email(user):
    token =user.get_reset_token()
    msg = Message('Password Reset Request',sender='a1.kungfupanda@gmail.com',recipients=[user.email])
    msg.body = f'''To reset your password , visit  the following link :
    {url_for('reset_token',token = token,_external=True)}
    If you not make this request then simply ignore this email and no change made.'''
    mail.send(msg)


@app.route("/reset_password",methods= ['GET', 'POST'])
def reset_request():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RequestResetForm()
    if form. validate_on_submit():
        user = Register.query.filter_by(email =form.email.data).first()
        send_reset_email(user)
        flash('An email has been sent with instrictions to reset password', 'info')
        return redirect(url_for('customerLogin'))
    return render_template('reset_password.html',title='Resert Password', form =form)

@app.route("/reset_password/<token>",methods= ['GET', 'POST'])
def reset_token(token):
   if current_user.is_authenticated:
       return redirect(url_for('index'))
   user = Register.verify_reset_token(token)
   if user is None:
       flash('That is an invalid or expired token', 'warning')
       return redirect(url_for('reset_request'))
   form = ResetPasswordForm()
   if form.validate_on_submit():
       hash_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
       user.password = hash_password
       db.session.commit()
       flash('You password has been update! You are now able to log in' ,'success')
       return redirect(url_for('customerLogin'))
   return render_template('reset_token.html', title='Resert Password', form=form)


@app.route('/contact', methods=['POST', 'GET'])
def contact():
    posts = Post.query.order_by(Post.id.desc()).all()
    random_post = random.sample(list(posts), 2)
    print(random_post)
    form = ContactForm()
    if form.validate_on_submit():
        print('-------------------------')
        print(request.form['name'])
        print(request.form['email'])
        print(request.form['subject'])
        print(request.form['message'])
        print('-------------------------')
        send_message(request.form)
        return redirect('/success')

    return render_template('contact.html', form=form,posts= random_post)

@app.route('/success')
def success():
    return render_template('/index.html')

def send_message(message):
    print(message.get('name'))

    msg = Message(message.get('subject'), sender = message.get('email'),
            recipients = ['a1.kungfupanda@gmail.com'],
            body= message.get('message')
    )
    mail.send(msg)


@app.route('/blog')
def Blog():
    posts = Post.query.order_by(Post.id.desc()).all()
    random_post = random.sample(list(posts), 2)
    print(random_post)
    post = Post.query.order_by(Post.id.desc()).all()
    return render_template('blog.html', post=post,posts= random_post)

# remove un wanted detail from shopping cart
def updateshoppingcart():
    for _key, product in session['Shoppingcart'].items():
        session.modified =True
        del product['image']
        del product['colors']
    return updateshoppingcart


@app.route('/getorder')
@login_required
def get_order():
    if current_user.is_authenticated:
        customer_id = current_user.id
        invoice = secrets.token_hex(5)
        updateshoppingcart()
        try:
            order = CustomerOrder(invoice=invoice, customer_id=customer_id, orders=session['Shoppingcart'])
            db.session.add(order)
            db.session.commit()
            session.pop('Shoppingcart')
            flash('Your order has been sent successfully', 'success')
            return redirect(url_for('orders', invoice=invoice))
        except Exception as e:
            print(e)
            flash('Some thing went wrong while get order', 'danger')
            return redirect(url_for('getCart'))


@app.route('/orders/<invoice>')
@login_required
def orders(invoice):
    if current_user.is_authenticated:
        grandTotal = 0
        subTotal = 0
        customer_id = current_user.id
        customer = Register.query.filter_by(id=customer_id).first()
        orders = CustomerOrder.query.filter_by(customer_id=customer_id, invoice=invoice).order_by(CustomerOrder.id.desc()).first()
        for _key, product in orders.orders.items():
            discount = (product['discount'] / 100) * float(product['price'])
            subTotal += float(product['price']) * int(product['quantity'])
            subTotal -= discount
            tax = ("%.2f" % (.06 * float(subTotal)))
            grandTotal = ("%.2f" % (int(subTotal)))
    else:
        return redirect(url_for('customerLogin'))
    return render_template('order.html', invoice=invoice, tax=tax, subTotal=subTotal, grandTotal=grandTotal,
                           customer=customer, orders=orders)
@app.route('/search')
def search():
    posts = Post.query.order_by(Post.id.desc()).all()
    random_post = random.sample(list(posts), 2)
    print(random_post)
    keyword = request.args.get('q')
    products = Addproduct.query.msearch(keyword, fields=['discription'], limit=6)
    return render_template('search.html',products=products,posts=random_post)


@app.route('/news/<int:id>', methods=['POST','GET'])
def news(id):
    post = Post.query.get_or_404(id)
    comment = Comments.query.filter_by(post_id=post.id).filter_by(feature=True).all()
    post.views = post.views + 1
    db.session.commit()
    Thanks =""
    if request.method =="POST":
        post_id = post.id
        name = request.form.get('name')
        email = request.form.get('email')
        message = request.form.get('message')
        comment = Comments(name=name,email=email,message=message,post_id=post_id)
        db.session.add(comment)
        post.comments = post.comments + 1
        db.session.commit()
        flash('Your comment has been submited  submitted will be published after aproval of admin', 'success')
        return redirect(request.url)

    return render_template('news-details.html', post=post, comment=comment, Thanks=Thanks)

@app.route('/get_pdf/<invoice>', methods=['POST'])
@login_required
def get_pdf(invoice):
    if current_user.is_authenticated:
        grandTotal = 0
        subTotal = 0
        customer_id = current_user.id
        if request.method =="POST":
            customer = Register.query.filter_by(id=customer_id).first()
            orders = CustomerOrder.query.filter_by(customer_id=customer_id, invoice=invoice).order_by(CustomerOrder.id.desc()).first()
            for _key, product in orders.orders.items():
                discount = (product['discount']/100) * float(product['price'])
                subTotal += float(product['price']) * int(product['quantity'])
                subTotal -= discount

                grandTotal = float("%.2f" % (subTotal))

            rendered =render_template('pdf.html', invoice=invoice,grandTotal=grandTotal,customer=customer,orders=orders)
            pdf = pdfkit.from_string(rendered, False)
            response = make_response(pdf)
            response.headers['content-Type'] ='application/pdf'
            response.headers['content-Disposition'] ='inline; filename=' + invoice +'.pdf'
            return response
    return request(url_for('orders'))
#login github
@app.route('/github')
def github_login():
      if not github.authorized:
            return redirect(url_for("github.login"))
      account_info=github.get("/user")
      if account_info.ok:
            account_info_json = account_info.json()
            return '<h1>Your Github name is {} '.format(account_info_json['login'])
      return '<h1>Request failed</h1>'
#search





