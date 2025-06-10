import os
import logging
import traceback
from flask import Flask
from sqlalchemy.engine import Engine
from sqlalchemy import event
from abilities import apply_sqlite_migrations
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
from abilities import apply_sqlite_migrations  # Absolute import

# Initialize SQLAlchemy
db = SQLAlchemy()

# Configure logging
logging.basicConfig(
    level=logging.INFO, 
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()

app = Flask(__name__, template_folder='../templates', static_folder='../static')

# Set Flask secret key with enhanced logging
try:
    secret_key = os.environ.get('FLASK_SECRET_KEY')
    if not secret_key:
        logger.warning("No FLASK_SECRET_KEY found. Using default secret key.")
        secret_key = 'supersecretflaskskey'
    app.config['SECRET_KEY'] = secret_key
except Exception as e:
    logger.error(f"Error setting secret key: {e}")
    logger.error(traceback.format_exc())

# Initialize database with absolute path
import os
database_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'instance', 'your_database.db')
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{database_path}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

# Initialize Login Manager with enhanced error handling and logging
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'  # Must match the route name in routes.py
login_manager.login_message = 'Please log in to access this page'
login_manager.login_message_category = 'info'

# Add debug logging for route registration
logger.info("Registered routes:")
for rule in app.url_map.iter_rules():
    logger.info(f"Route: {rule.endpoint} -> {rule.rule}")

# Apply database migrations with enhanced error handling
try:
    with app.app_context():
        logger.info("Starting database migration process")
        # Create all tables if they don't exist
        db.create_all()
        # Apply migrations
        apply_sqlite_migrations(db.engine, db.Model, '../migrations')
        logger.info("Database migrations completed successfully")
except Exception as e:
    logger.error(f"Database migration failed: {e}")
    logger.error(traceback.format_exc())

@login_manager.user_loader
def load_user(user_id):
    try:
        from models import User
        user = User.query.get(int(user_id))
        if user:
            logger.debug(f"User {user_id} loaded successfully")
        else:
            logger.warning(f"No user found with ID {user_id}")
        return user
    except Exception as e:
        logger.error(f"Error loading user {user_id}: {e}")
        logger.error(traceback.format_exc())
        return None
