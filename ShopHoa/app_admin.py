from flask import render_template, request, session, redirect, url_for, flash,current_app
from ShopHoa import app, bcrypt,photos,db
from ShopHoa.repository.form import *
from ShopHoa.repository.models import *
from flask_login import current_user,login_user,logout_user,login_required
import secrets,os

def save_photo(photo):
    rand_hex  = secrets.token_hex(10)
    _, file_extention = os.path.splitext(photo.filename)
    file_name = rand_hex + file_extention
    file_path = os.path.join(current_app.root_path, 'static/images', file_name)
    photo.save(file_path)
    return file_name


@app.route('/admin/')
def admin_index():
    if 'email' not in session:
        flash(f'Vui lòng đăng nhập trước', 'danger')
        return redirect(url_for('admin_login'))
    products = Addproduct.query.all()
    return render_template("admin/index_admin.html",products = products)

@app.route('/admin/user')
def admin_user():
    if 'email' not in session:
        flash(f'Vui lòng đăng nhập trước', 'danger')
        return redirect(url_for('admin_login'))
    user = Register.query.all()
    return render_template("admin/user.html",user = user)

@app.route("/admin/brands", methods=["GET", "POST"])
def admin_brands():
    if 'email' not in session:
        flash(f'Vui lòng đăng nhập trước', 'danger')
        return redirect(url_for('admin_login'))
    brands = Brand.query.order_by(Brand.id.desc()).all()
    return render_template('admin/brands.html', brands=brands)





@app.route("/admin/category", methods=["GET", "POST"])
def admin_category():
    if 'email' not in session:
        flash(f'Vui lòng đăng nhập trước', 'danger')
        return redirect(url_for('admin_login'))
    categories = Category.query.order_by(Category.id.desc()).all()
    return render_template('admin/brands.html',categories=categories)

@app.route("/admin/register", methods=["GET", "POST"])
def admin_register():
    form = RegistrationForm(request.form)
    if request.method == 'POST' and form.validate():
        hash_password = bcrypt.generate_password_hash(form.password.data)
        user = User(name = form.name.data,username=form.username.data, email=form.email.data,password=hash_password)
        db.session.add(user)
        db.session.commit()
        flash(f'Chào bạn,{form.username.data} ,Bạn đăng ký thành công',"Success")
        return redirect(url_for('admin_login'))
    return render_template("admin/register.html",form= form)

@app.route("/admin/login", methods=["GET", "POST"])
def admin_login():
    form = LoginForm(request.form)
    if request.method == "POST" and form.validate():
        user = User.query.filter_by(email = form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            session['email'] = form.email.data
            flash(f'Chào bạn,{form.email.data} , đã login', 'Success')
            return redirect(request.args.get('next') or url_for('admin_index'))
        else:
            flash('Mật khẩu sai vui lòng thử lại','danger')

    return render_template("admin/login.html",form= form)

@app.route("/admin/addbrand", methods=["GET", "POST"])
def admin_addbrand():
    if 'email' not in session:
        flash(f'Vui lòng đăng nhập trước', 'danger')
        return redirect(url_for('admin_login'))
    if request.method == "POST":
        getbrand = request.form.get('brand')
        brand = Brand(name= getbrand)
        db.session.add(brand)
        flash(f' nhãn {getbrand} đã được thêm vào database ', 'success')
        db.session.commit()
        return redirect(url_for('admin_addbrand'))
    return render_template('admin/addbrand.html',brands= 'brands')

@app.route("/admin/updatebrand/<int:id>", methods=["GET", "POST"])
def admin_updatebrands(id):
    if 'email' not in session:
        flash(f'Vui lòng đăng nhập trước', 'danger')
    updatebrand = Brand.query.get_or_404(id)
    brand =request.form.get('brand')
    if request.method == 'POST':
        updatebrand.name =brand
        flash("Thương hiệu của bạn đã được cập nhật",'success')
        db.session.commit()
        return redirect(url_for('admin_brands'))
    return render_template('admin/updatebrand.html', updatebrand = updatebrand)


@app.route("/admin/deletebrand/<int:id>", methods=["GET", "POST"])
def admin_deletebrand(id):
    brand = Brand.query.get_or_404(id)
    if request.method == "POST":
        db.session.delete(brand)
        db.session.commit()
        flash(f'Thương hiệu {brand.name} xóa khỏi database của bạn ','success')
        return redirect(url_for('admin_brands'))
    flash(f'Thương hiệu {brand.name} có thể bị xóa', 'wraning')
    return redirect(url_for('admin_brands'))

@app.route("/admin/addcat", methods=["GET", "POST"])
def admin_addcat():
    if 'email' not in session:
        flash(f'Vui lòng đăng nhập trước', 'danger')
        return redirect(url_for('admin_login'))
    if request.method == "POST":
        getbrand = request.form.get('category')
        cat = Category(name= getbrand)
        db.session.add(cat)
        flash(f' Loại {getbrand} đã được thêm vào database ', 'success')
        db.session.commit()
        return redirect(url_for('admin_addcat'))
    return render_template('admin/addbrand.html')

@app.route("/admin/updatecat/<int:id>", methods=["GET", "POST"])
def admin_updatecat(id):
    if 'email' not in session:
        flash(f'Vui lòng đăng nhập trước', 'danger')
    updatecat = Category.query.get_or_404(id)
    category =request.form.get('category')
    if request.method == 'POST':
        updatecat.name =category
        flash("Category của bạn đã được cập nhật",'success')
        db.session.commit()
        return redirect(url_for('admin_category'))
    return render_template('admin/updatebrand.html', updatecat = updatecat)

@app.route("/admin/deletecategory/<int:id>", methods=["GET", "POST"])
def admin_deletecategory(id):
    category = Category.query.get_or_404(id)
    if request.method == "POST":
        db.session.delete(category)
        db.session.commit()
        flash(f'Thể loại {category.name} xóa khỏi database của bạn ','success')
        return redirect(url_for('admin_brands'))
    flash(f'Thể loại {category.name} có thể bị xóa', 'wraning')
    return redirect(url_for('admin_brands'))

@app.route("/admin/addproduct", methods=["GET", "POST"])
def admin_addproduct():
    if 'email' not in session:
        flash(f'Vui lòng đăng nhập trước', 'danger')
        return redirect(url_for('admin_login'))
    brands = Brand.query.all()
    categories = Category.query.all()
    form = Addproducts(request.form)
    if request.method == 'POST':
        name = form.name.data
        price = form .price.data
        discount = form.discount.data
        stock = form.stock.data
        color = form.color.data
        discription = form.discription.data
        brand = request.form.get('brand')
        category = request.form.get('category')

        image_1 = photos.save(request.files.get('image_1'), name=secrets.token_hex(10) + ".")
        image_2 = photos.save(request.files.get('image_2'), name=secrets.token_hex(10) + ".")
        image_3 = photos.save(request.files.get('image_3'), name=secrets.token_hex(10) + ".")

        addpro = Addproduct(name = name, price = price, discount = discount, stock =stock, color = color,
                             discription = discription,brand_id= brand, category_id = category,image_1 = image_1,image_2 = image_2,image_3 = image_3)
        db.session.add(addpro)
        flash(f'Sản phẩm {name} đã được thêm vào database', 'success')
        db.session.commit()
        return redirect(url_for('admin_index'))
    return render_template('admin/addproduct.html',form = form,brands = brands, categories = categories)


@app.route("/admin/updateproduct/<int:id>", methods=["GET", "POST"])
def admin_updateproduct(id):
    brands = Brand.query.all()
    categories = Category.query.all()
    product = Addproduct.query.get_or_404(id)
    brand =request.form.get('brand')
    category =request.form.get('category')
    form = Addproducts(request.form)
    if request.method == "POST":
        product.name = form.name.data
        product.price = form.price.data
        product.discount = form.discount.data
        product.brand_id = brand
        product.category_id = category
        product.color = form.color.data
        product.discription = form.discription.data
        if request.files.get('image_1'):
            try:
                os.unlink(os.path.join(current_app.root_path,"static/images/" + product.image_1))
                product.image_1 = photos.save(request.files.get('image_1'),name=secrets.token_hex(10) + ".")
            except:
                product.image_1 = photos.save(request.files.get('image_1'), name=secrets.token_hex(10) + ".")
        if request.files.get('image_2'):
            try:
                os.unlink(os.path.join(current_app.root_path,"static/images/" + product.image_2))
                product.image_1 = photos.save(request.files.get('image_2'),name=secrets.token_hex(10) + ".")
            except:
                product.image_1 = photos.save(request.files.get('image_2'), name=secrets.token_hex(10) + ".")
        if request.files.get('image_3'):
            try:
                os.unlink(os.path.join(current_app.root_path,"static/images/" + product.image_3))
                product.image_1 = photos.save(request.files.get('image_3'),name=secrets.token_hex(10) + ".")
            except:
                product.image_1 = photos.save(request.files.get('image_3'), name=secrets.token_hex(10) + ".")
        db.session.commit()
        flash(f'Sản phẩm của bạn đa được update', 'success')
        return redirect(url_for('admin_index'))

    form.name.data = product.name
    form.price.data = product.price
    form.discount.data = product.discount
    form.stock.data = product.stock
    form.color.data = product.color
    form.discription.data = product.discription
    return render_template('admin/updateproduct.html',form = form, brands = brands, categories = categories,product = product)

@app.route("/admin/deleteproduct/<int:id>", methods=[ "POST"])
def admin_deleteproduct(id):
    product = Addproduct.query.get_or_404(id)
    if request.method == "POST":
        if request.files.get('image_1'):
            try:
                os.unlink(os.path.join(current_app.root_path,"static/images/" + product.image_1))
                os.unlink(os.path.join(current_app.root_path,"static/images/" + product.image_2))
                os.unlink(os.path.join(current_app.root_path,"static/images/" + product.image_3))
            except Exception as e:
                print(e)
        db.session.delete(product)
        db.session.commit()
        flash(f'Sản phẩm {product.name} xóa khỏi database của bạn ','success')
        return redirect(url_for('admin_index'))
    flash(f'Sản phẩm {product.name} có thể bị xóa', 'danger')
    return redirect(url_for('admin_index'))

@app.route('/admin/post')
def admin():
    posts = Post.query.order_by(Post.id.desc()).all()
    return render_template('admin/blog.html',posts = posts)


@app.route('/admin/comments', methods=['POST','GET'])
def comments():
    comments =Comments.query.order_by(Comments.id.desc()).all()
    return render_template('admin/comment.html',comments=comments)


@app.route('/check/<int:id>', methods=['POST','GET'])

def check(id):
    comment = Comments.query.get_or_404(id)
    if (comment.feature == True):
        comment.feature = False
        db.session.commit()
    else:
        comment.feature = True
        db.session.commit()
        return redirect(url_for('comments'))
    return redirect(url_for('comments'))


@app.route('/admin/addpost',methods=['POST','GET'])
def addpost():
    form = PostForm(request.form)
    if request.method =="POST" and form.validate():
        photo = save_photo(request.files.get('photo'))
        post = Post(title=form.title.data,
                    body=form.content.data,category=request.form.get('category'),
                    image=photo)
        db.session.add(post)
        db.session.commit()
        flash('Your post has been added ','success')
        return redirect(url_for('admin'))
    return render_template('admin/addpost.html', form=form)


@app.route('/update/<int:id>',methods=['POST','GET'])
def update(id):
    form = PostForm(request.form)
    post = Post.query.get_or_404(id)
    form.title.data = post.title
    form.content.data = post.body
    if request.method=='POST' and form.validate():
        if request.files.get('photo'):
            try:
                os.unlink(os.path.join(current_app.root_path, 'static/images/'+ post.image))
                post.image = save_photo(request.files.get('photo'))
            except:
                post.image = save_photo(request.files.get('photo'))
        post.title = form.title.data
        post.body = form.content.data
        post.category = request.form.get('category')
        flash('Post has been updated', 'success')
        db.session.commit()
        return redirect(url_for('admin'))
    return render_template('admin/addpost.html', form=form, post=post)


@app.route('/delete/<int:id>')
def delete(id):
    post = Post.query.get_or_404(id)
    try:
        os.unlink(os.path.join(current_app.root_path,'static/images/'+ post.image))
        db.session.delete(post)
    except:
        db.session.delete(post)
    flash('Post has deleted ','success')
    db.session.commit()
    return redirect(url_for('admin'))

@app.route('/delcomment/<int:id>')
@login_required
def delcomment(id):
    comment = Comments.query.get_or_404(id)
    db.session.delete(comment)
    db.session.commit()
    flash('Comment has deleted ','success')
    return redirect(url_for('admin'))


@app.route('/admin/chat')
def chat():
    return render_template('admin/chat.html')