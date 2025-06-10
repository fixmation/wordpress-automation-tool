from flask import Flask, render_template
from flask_login import LoginManager, current_user, login_required
import os

# Initialize Flask app with correct template path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TEMPLATE_DIR = os.path.join(BASE_DIR, 'WordPressAutomationTool', 'templates')

app = Flask(__name__, template_folder=TEMPLATE_DIR)
app.secret_key = os.environ.get('SECRET_KEY', 'dev-key-change-in-production')

# Flask-Login setup
login_manager = LoginManager(app)
login_manager.login_view = 'index'  # Set to 'index' which exists

# Remove the placeholder login route to avoid confusion
# @app.route('/login', methods=['GET', 'POST'])
# def login():
#     # Placeholder login route for demonstration
#     from flask import request, redirect, url_for, flash
#     from flask_login import login_user
#     if request.method == 'POST':
#         # Implement actual authentication logic here
#         # For now, just flash a message and redirect to home
#         flash('Login functionality not implemented yet.')
#         return redirect(url_for('home'))
#     return '''
#     <form method="post">
#         <input type="text" name="username" placeholder="Username" required/>
#         <input type="password" name="password" placeholder="Password" required/>
#         <button type="submit">Login</button>
#     </form>
#     '''

@login_manager.user_loader
def load_user(user_id):
    # Replace this with your actual user loading logic
    # For now, return None to avoid errors
    return None

@app.route('/')
def index():
    return 'Welcome to the app. Please <a href="/login">login</a>.'

# Remove the duplicate home route with login_required to avoid conflict
# @app.route('/')
# @login_required
# def home():
#     try:
#         return render_template('home.html', current_user=current_user)
#     except Exception as e:
#         app.logger.error(f"Template rendering failed: {str(e)}")
#         return render_template('error.html',
#                            error_message=str(e),
#                            template_path=TEMPLATE_DIR,
#                            available_templates=os.listdir(TEMPLATE_DIR)), 500
    except Exception as e:
        app.logger.error(f"Template rendering failed: {str(e)}")
        return render_template('error.html',
                           error_message=str(e),
                           template_path=TEMPLATE_DIR,
                           available_templates=os.listdir(TEMPLATE_DIR)), 500

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

from flask import request, redirect, url_for, flash
from WordPressAutomationTool.CrossPlatform import CrossPlatformBuilder

builder = CrossPlatformBuilder()

@app.route('/cross_platform_builder/create', methods=['POST'])
@login_required
def create_website():
    platform = request.form.get('platform')
    website_name = request.form.get('website_name')
    description = request.form.get('description')

    if not platform or not website_name or not description:
        flash('All fields are required.')
        return redirect(url_for('cross_platform_builder'))

    # TODO: Implement website creation logic using CrossPlatformBuilder
    # For now, just flash a success message and redirect back
    flash(f'Website "{website_name}" creation initiated for platform: {platform}.')
    return redirect(url_for('cross_platform_builder'))

@app.route('/debug')
def debug():
    return {
        "status": "success",
        "template_path": TEMPLATE_DIR,
        "dir_exists": os.path.exists(TEMPLATE_DIR),
        "files": sorted(os.listdir(TEMPLATE_DIR)),
        "authentication": {
            "is_authenticated": current_user.is_authenticated,
            "user_id": current_user.get_id() if current_user.is_authenticated else None
        }
    }

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
