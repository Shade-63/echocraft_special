import cloudinary.uploader
from flask import render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_user, logout_user, login_required, current_user
from extensions import db
from models import User, Post
from forms import LoginForm, PostForm
from werkzeug.utils import secure_filename
import os
import cloudinary
from sqlalchemy.exc import IntegrityError

def init_routes(app):
    @app.route('/')
    def home():
        try:
            category = request.args.get('category')
            query = Post.query
            if category:
                query = query.filter_by(category=category)
            posts = query.order_by(Post.created_at.desc()).all()
            return render_template('index.html', posts=posts, active_category=category)
        except Exception as e:
            flash('An error occurred while loading posts. Please try again.', 'danger')
            return render_template('index.html', posts=[], active_category=None)

    @app.route('/login', methods=['GET', 'POST'])
    def login():
        form = LoginForm()
        if form.validate_on_submit():
            try:
                user = User.query.filter_by(username=form.username.data).first()
                if user and user.check_password(form.password.data):
                    login_user(user)
                    flash(f'Welcome back, {user.username}!', 'success')
                    return redirect(url_for('home'))
                else:
                    flash('Invalid username or password. Please try again.', 'danger')
            except Exception as e:
                flash('An error occurred during login. Please try again.', 'danger')
        elif form.errors:
            # Display form validation errors
            for field, errors in form.errors.items():
                for error in errors:
                    flash(f'{getattr(form, field).label.text}: {error}', 'danger')
        
        return render_template('login.html', form=form)

    @app.route('/signup', methods=['GET', 'POST'])
    def signup():
        form = LoginForm()
        if form.validate_on_submit():
            try:
                # Check if username already exists
                existing_user = User.query.filter_by(username=form.username.data).first()
                if existing_user:
                    flash('Username already exists. Please choose a different one.', 'danger')
                    return render_template('signup.html', form=form)
                
                # Create new user with hashed password
                user = User(username=form.username.data)
                user.set_password(form.password.data)
                db.session.add(user)
                db.session.commit()
                
                flash('Account created successfully! Please login.', 'success')
                return redirect(url_for('login'))
                
            except IntegrityError:
                db.session.rollback()
                flash('Username already exists. Please choose a different one.', 'danger')
            except Exception as e:
                db.session.rollback()
                flash('An error occurred while creating your account. Please try again.', 'danger')
        elif form.errors:
            # Display form validation errors
            for field, errors in form.errors.items():
                for error in errors:
                    flash(f'{getattr(form, field).label.text}: {error}', 'danger')
        
        return render_template('signup.html', form=form)

    @app.route('/create', methods=['GET', 'POST'])
    @login_required
    def create_post():
        form = PostForm()
        if form.validate_on_submit():
            try:
                img_url = None
                if form.image.data:
                    # Validate file type
                    allowed_extensions = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
                    filename = form.image.data.filename
                    if filename and '.' in filename:
                        file_ext = filename.rsplit('.', 1)[1].lower()
                        if file_ext not in allowed_extensions:
                            flash('Invalid file type. Please upload PNG, JPG, JPEG, GIF, or WebP images only.', 'danger')
                            return render_template('create.html', form=form)
                    
                    # Validate file size (5MB limit)
                    if form.image.data.content_length > 5 * 1024 * 1024:  # 5MB
                        flash('File size too large. Please upload images smaller than 5MB.', 'danger')
                        return render_template('create.html', form=form)
                    
                    try:
                        result = cloudinary.uploader.upload(
                            form.image.data,
                            folder="echocraft_uploads"
                        )
                        img_url = result['secure_url']
                    except Exception as e:
                        flash('Image upload failed. Please try again.', 'danger')
                        return render_template('create.html', form=form)

                post = Post(
                    title=form.title.data.strip(),
                    content=form.content.data.strip() if form.content.data else '',
                    category=form.category.data,
                    img_url=img_url,
                    author=current_user
                )
                db.session.add(post)
                db.session.commit()
                
                flash('Post created successfully!', 'success')
                return redirect(url_for('home'))
                
            except Exception as e:
                db.session.rollback()
                flash('An error occurred while creating your post. Please try again.', 'danger')
        elif form.errors:
            # Display form validation errors
            for field, errors in form.errors.items():
                for error in errors:
                    flash(f'{getattr(form, field).label.text}: {error}', 'danger')
        
        return render_template('create.html', form=form)
    
    @app.route('/post/<int:post_id>')
    def post_detail(post_id):
        try:
            post = Post.query.get_or_404(post_id)
            return render_template('post_detail.html', post=post)
        except Exception as e:
            flash('Post not found or an error occurred.', 'danger')
            return redirect(url_for('home'))
    
    @app.route('/react/<int:post_id>/<reaction>', methods=['POST'])
    @login_required
    def react(post_id, reaction):
        try:
            post = Post.query.get_or_404(post_id)
            if reaction in ['likes', 'funny', 'inspire']:
                setattr(post, reaction, getattr(post, reaction) + 1)
                db.session.commit()
                return jsonify({'new_count': getattr(post, reaction)})
            else:
                return jsonify({'error': 'Invalid reaction'}), 400
        except Exception as e:
            return jsonify({'error': 'An error occurred'}), 500
    
    @app.route('/post_delete/<int:post_id>', methods=['GET', 'POST'])
    @login_required
    def post_delete(post_id):
        try:
            post = Post.query.get_or_404(post_id)
            if post.author.id != current_user.id:
                flash('You cannot delete posts that are not yours.', 'danger')
                return redirect(url_for('home'))
            
            db.session.delete(post)
            db.session.commit()
            flash('Post deleted successfully!', 'success')
            return redirect(url_for('home'))
        except Exception as e:
            flash('An error occurred while deleting the post.', 'danger')
            return redirect(url_for('home'))

    @app.route('/logout')
    def logout():
        logout_user()
        flash('You have been logged out successfully.', 'info')
        return redirect(url_for('home'))