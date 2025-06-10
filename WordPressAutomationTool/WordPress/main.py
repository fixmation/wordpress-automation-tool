import os
from app_init import app, db
from models import User  # Import User model after db is initialized
import routes  # Import routes after models

if __name__ == '__main__':
    # Load configuration based on environment
    env = os.getenv('FLASK_ENV', 'development')
    if env == 'production':
        app.config.from_object('config.ProductionConfig')
    else:
        app.config.from_object('config.DevelopmentConfig')

    # Ensure database file exists and tables are created
    with app.app_context():
        # Create instance directory if it doesn't exist
        instance_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'instance')
        os.makedirs(instance_dir, exist_ok=True)

        # Ensure tables are created
        db.create_all()

        # Check if we have any users, create admin if none
        from models import User
        if User.query.count() == 0:
            print("Creating default admin user...")
            admin = User(email="admin@example.com", is_admin=True)
            admin.set_password("admin123")
            db.session.add(admin)
            db.session.commit()
            print("Default admin created with email: admin@example.com and password: admin123")

    print("Starting server on port 5000")
    try:
        # We don't need to kill existing processes on Replit
        # Binding to 0.0.0.0 ensures the app is accessible externally
        app.run(host='0.0.0.0', port=5000, debug=True)
    except OSError as e:
        if "Address already in use" in str(e):
            print("Port 5000 is already in use. Trying alternative port 8080...")
            app.run(host='0.0.0.0', port=8080, debug=True)
        else:
            print(f"Error starting server: {e}")