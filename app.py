from dotenv import load_dotenv
load_dotenv()
from flask import Flask
from extensions import db, login_manager
from models import User
import cloudinary
import cloudinary.uploader
import os

def create_app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'ZORO-63')
    
    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'login'

    cloudinary.config(
    cloud_name= "echocraft",
    api_key= "111945726124917",
    api_secret= "J0ZEBLtm_ulWqRWHiT5Mzz0wCDk",
    )


    # Must define user_loader INSIDE create_app before routes
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))
    
    # Register routes
    from routes import init_routes
    init_routes(app)
    
    # Create tables
    with app.app_context():
        db.create_all()
    
    return app

app = create_app()

if __name__ == '__main__':
    app.run(debug=True)