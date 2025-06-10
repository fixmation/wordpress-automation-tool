from flask import Flask, render_template, request, redirect, url_for, flash
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
import os

# Initialize Flask app with correct template path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TEMPLATE_DIR = os.path.join(BASE_DIR, 'WordPressAutomationTool', 'templates')

import logging

app = Flask(__name__, template_folder=TEMPLATE_DIR)
app.secret_key = os.environ.get('SECRET_KEY', 'dev-key-change-in-production')

# Setup logging
logging.basicConfig(level=logging.DEBUG)

# Flask-Login setup
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Simple User class for demonstration
class User(UserMixin):
    def __init__(self, user_id):
        self.id = user_id

# Dummy user database
users = {'admin': {'password': 'admin'}}

@login_manager.user_loader
def load_user(user_id):
    if user_id in users:
        return User(user_id)
    return None

@app.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        app.logger.debug(f"Login attempt for user: {username}")
        
        if username in users and users[username]['password'] == password:
            user = User(username)
            login_user(user)
            app.logger.debug(f"User {username} logged in successfully")
            return redirect(url_for('dashboard'))
        
        flash('Invalid credentials')
    
    return '''
        <!DOCTYPE html>
        <html>
        <head>
            <title>Login - WordPress Automation Tool</title>
            <style>
                body {
                    font-family: Arial, sans-serif;
                    margin: 0;
                    padding: 0;
                    display: flex;
                    justify-content: center;
                    align-items: center;
                    min-height: 100vh;
                    background-color: #f0f2f5;
                }
                .container {
                    background-color: white;
                    padding: 40px;
                    border-radius: 8px;
                    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
                    width: 100%;
                    max-width: 400px;
                }
                h1 {
                    margin: 0 0 24px 0;
                    color: #1a1a1a;
                    font-size: 24px;
                    text-align: center;
                }
                .form-group {
                    margin-bottom: 16px;
                }
                input {
                    width: 100%;
                    padding: 12px;
                    border: 1px solid #ddd;
                    border-radius: 4px;
                    box-sizing: border-box;
                    font-size: 16px;
                }
                input:focus {
                    outline: none;
                    border-color: #0066cc;
                }
                button {
                    width: 100%;
                    padding: 12px;
                    background-color: #0066cc;
                    color: white;
                    border: none;
                    border-radius: 4px;
                    font-size: 16px;
                    cursor: pointer;
                    transition: background-color 0.2s;
                }
                button:hover {
                    background-color: #0052a3;
                }
            </style>
        </head>
        <body>
            <div class="container">
                <h1>Login</h1>
                <form method="post">
                    <div class="form-group">
                        <input type="text" name="username" placeholder="Username" required>
                    </div>
                    <div class="form-group">
                        <input type="password" name="password" placeholder="Password" required>
                    </div>
                    <button type="submit">Login</button>
                </form>
            </div>
        </body>
        </html>
    '''

@app.route('/dashboard')
@login_required
def dashboard():
    return f'''
        <h1>Welcome, {current_user.id}!</h1>
        <p><a href="/cross_platform_builder">Go to Cross Platform Builder</a></p>
        <p><a href="/logout">Logout</a></p>
    '''

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/cross_platform_builder')
@login_required
def cross_platform_builder():
    try:
        return render_template('cross_platform_builder.html', current_user=current_user)
    except Exception as e:
        app.logger.error(f"Template rendering failed: {str(e)}")
        return render_template('error.html',
                           error_message=str(e),
                           template_path=TEMPLATE_DIR,
                           available_templates=os.listdir(TEMPLATE_DIR)), 500

@app.route('/cross_platform_builder/create', methods=['POST'])
@login_required
def create_website():
    platform = request.form.get('platform')
    website_name = request.form.get('website_name')
    description = request.form.get('description')

    if not platform or not website_name or not description:
        flash('All fields are required.')
        return redirect(url_for('cross_platform_builder'))

    flash(f'Website "{website_name}" creation initiated for platform: {platform}.')
    return redirect(url_for('cross_platform_builder'))

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 8000))
    app.run(host='0.0.0.0', port=port)
