from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from app_init import db

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    is_admin = db.Column(db.Boolean, default=False, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    last_login = db.Column(db.DateTime)
    login_attempts = db.Column(db.Integer, default=0)
    # mfa_secret removed as not needed
    server_connections = db.relationship('ServerConnection', backref='user', lazy=True)
    subscription_plans = db.relationship('SubscriptionPlan', backref='user', lazy=True)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
        
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
        
    def record_login(self):
        self.last_login = datetime.utcnow()
        self.login_attempts = 0
        # No commit here - caller should handle the commit
        
    def record_failed_attempt(self):
        self.login_attempts += 1
        db.session.commit()

class ServerConnection(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    domain_name = db.Column(db.String(255), nullable=False)
    cpanel_username = db.Column(db.String(255), nullable=False)
    cpanel_password = db.Column(db.String(255), nullable=False)
    cpanel_api_key = db.Column(db.String(255))
    softaculous_api_key = db.Column(db.String(255))
    ssh_details = db.Column(db.Text)
    installation_method = db.Column(db.String(50), default='api')
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    last_verified = db.Column(db.DateTime)
    status = db.Column(db.String(50), default='pending')
    wordpress_installations = db.relationship('WordPressInstallation', backref='server', lazy=True)

class WebsiteCategory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    themes = db.relationship('Theme', backref='category', lazy=True)
    wordpress_installations = db.relationship('WordPressInstallation', backref='category', lazy=True)

class Theme(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=False)
    thumbnail_url = db.Column(db.String(255), nullable=False)
    demo_url = db.Column(db.String(255))
    category_id = db.Column(db.Integer, db.ForeignKey('website_category.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    status = db.Column(db.String(50), default='pending')
    wordpress_installations = db.relationship('WordPressInstallation', backref='theme', lazy=True)

class WordPressInstallation(db.Model):
    __tablename__ = 'wordpress_installation'
    id = db.Column(db.Integer, primary_key=True)
    server_id = db.Column(db.Integer, db.ForeignKey('server_connection.id'))
    site_url = db.Column(db.String(255), nullable=False)
    admin_username = db.Column(db.String(255), nullable=False)
    admin_password = db.Column(db.String(255), nullable=False)
    admin_email = db.Column(db.String(255), nullable=False)
    site_title = db.Column(db.String(255), nullable=False)
    status = db.Column(db.String(50), default='pending')
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    installed_at = db.Column(db.DateTime)
    category_id = db.Column(db.Integer, db.ForeignKey('website_category.id'))
    theme_id = db.Column(db.Integer, db.ForeignKey('theme.id'))
    
    def to_dict(self):
        """Convert model to dictionary for API responses"""
        return {
            'id': self.id,
            'server_id': self.server_id,
            'site_url': self.site_url,
            'admin_username': self.admin_username,
            'admin_email': self.admin_email,
            'site_title': self.site_title,
            'status': self.status,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'installed_at': self.installed_at.isoformat() if self.installed_at else None,
            'category_id': self.category_id,
            'theme_id': self.theme_id
        }
    
    def validate(self):
        """
        Validate WordPress installation data before saving
        
        Raises:
            ValueError: If validation fails
        """
        import re
        
        # Validate site URL
        url_pattern = re.compile(
            r'^(https?://)?'  # optional protocol
            r'([a-zA-Z0-9-]+\.)+[a-zA-Z]{2,}'  # domain
            r'(/[a-zA-Z0-9-./]*)?$'  # optional path
        )
        if not url_pattern.match(self.site_url):
            raise ValueError("Invalid site URL. Please provide a valid domain.")
        
        # Validate admin email
        email_pattern = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
        if not email_pattern.match(self.admin_email):
            raise ValueError("Invalid admin email address.")
        
        # Validate admin username
        if len(self.admin_username) < 3:
            raise ValueError("Admin username must be at least 3 characters long.")
        
        # Validate admin password complexity
        if len(self.admin_password) < 8:
            raise ValueError("Admin password must be at least 8 characters long.")
        
        # Validate site title
        if not self.site_title or len(self.site_title.strip()) == 0:
            raise ValueError("Site title cannot be empty.")
class SubscriptionPlan(db.Model):
    __tablename__ = 'subscription_plan'

    def to_dict(self):
        """Convert model to dictionary for API responses"""
        return {
            'id': self.id,
            'server_id': self.server_id,
            'site_url': self.site_url,
            'admin_username': self.admin_username,
            'admin_email': self.admin_email,
            'site_title': self.site_title,
            'status': self.status,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'installed_at': self.installed_at.isoformat() if self.installed_at else None,
            'category_id': self.category_id,
            'theme_id': self.theme_id
        }

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    stripe_customer_id = db.Column(db.String(255))
    stripe_subscription_id = db.Column(db.String(255))
    plan_type = db.Column(db.String(50), nullable=False)
    status = db.Column(db.String(50), default='active')
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    expires_at = db.Column(db.DateTime)
    current_stage = db.Column(db.Integer)
    stage_data = db.Column(db.Text)

class ChatMessage(db.Model):
    """Model for storing chat messages between users and AI assistant"""
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    message = db.Column(db.Text, nullable=False)
    response = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    user = db.relationship('User', backref=db.backref('chat_messages', lazy=True))


    def to_dict(self):
        """Convert model to dictionary for API responses"""
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


    def to_dict(self):
        """Convert model to dictionary for API responses"""
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'thumbnail_url': self.thumbnail_url,
            'demo_url': self.demo_url,
            'category_id': self.category_id,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'status': self.status
        }
