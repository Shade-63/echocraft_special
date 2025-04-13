import cloudinary.uploader
from flask import render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_user, logout_user, login_required, current_user
from extensions import db
from models import User, Post
from forms import LoginForm, PostForm
from werkzeug.utils import secure_filename
import os
import cloudinary

def init_routes(app):
    @app.route('/')
    def home():
        category = request.args.get('category')
        query = Post.query
        if category:
            query = query.filter_by(category = category)
        posts = query.order_by(Post.created_at.desc()).all()
        return render_template('index.html', posts=posts, active_category= category)

    @app.route('/login', methods=['GET', 'POST'])
    def login():
        form = LoginForm()
        if form.validate_on_submit():
            user = User.query.filter_by(username=form.username.data).first()
            if user and user.password == form.password.data:  # In production, use password hashing!
                login_user(user)
                return redirect(url_for('home'))
            flash('Invalid username or password', 'danger')
        return render_template('login.html', form=form)

    @app.route('/signup', methods=['GET', 'POST'])
    def signup():
        form = LoginForm()  # Reusing for simplicity
        if form.validate_on_submit():
            user = User(username=form.username.data, password=form.password.data)
            db.session.add(user)
            db.session.commit()
            flash('Account created! Please login', 'success')
            return redirect(url_for('login'))
        return render_template('signup.html', form=form)

    @app.route('/create', methods=['GET', 'POST'])
    @login_required
    def create_post():
        form = PostForm()
        if form.validate_on_submit():
            img_url = None
            if form.image.data:
                try:
                    result = cloudinary.uploader.upload(
                        form.image.data,
                        folder="echocraft_uploads"  # Organizinng uploads in Cloudinary
                    )
                    img_url = result['secure_url']
                except Exception as e:
                    flash('Image upload failed. Please try again.', 'danger')
                    return redirect(url_for('create_post'))

            post = Post(
                title=form.title.data,
                content=form.content.data,
                category=form.category.data,
                img_url= img_url,
                author= current_user
            )
            db.session.add(post)
            db.session.commit()
            flash('Post created!', 'success')
            return redirect(url_for('home'))
        return render_template('create.html', form=form)
    
    @app.route('/post/<int:post_id>')
    def post_detail(post_id):
        post = Post.query.get_or_404(post_id)
        return render_template('post_detail.html', post= post)
    
    @app.route('/react/<int:post_id>/<reaction>', methods= ['POST'])
    @login_required
    def react(post_id, reaction):
        post = Post.query.get_or_404(post_id)
        setattr(post, reaction, getattr(post, reaction) + 1)
        db.session.commit()
        return jsonify({'new_count': getattr(post, reaction)})
    
    @app.route('/post_delete/<int:post_id>', methods= ['GET', 'POST'])
    @login_required
    def post_delete(post_id):
        post = Post.query.get_or_404(post_id)
        if post.author.id != current_user.id:
            flash('You cannot delete others posts', 'danger')
            return redirect(url_for('home'))
        
        db.session.delete(post)
        db.session.commit()
        flash('Post deleted successfully', 'success')
        return redirect(url_for('home'))

    @app.route('/logout')
    def logout():
        logout_user()
        return redirect(url_for('home'))