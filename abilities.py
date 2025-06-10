# abilities.py - Database and WordPress automation functions

import sqlite3
from typing import Optional

def apply_sqlite_migrations(db_path: str, migrations_dir: str = "migrations") -> bool:
    """
    Applies SQLite migrations from .sql files in the specified directory
    Args:
        db_path: Path to SQLite database file
        migrations_dir: Directory containing migration SQL files (default: "migrations")
    Returns:
        bool: True if migrations succeeded, False otherwise
    """
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Get list of migration files sorted by name
        # (Assuming migration files are named like 001_initial.sql, 002_add_users.sql, etc.)
        migration_files = sorted(os.listdir(migrations_dir))
        
        for migration in migration_files:
            if migration.endswith('.sql'):
                with open(os.path.join(migrations_dir, migration), 'r') as f:
                    sql_script = f.read()
                    cursor.executescript(sql_script)
        
        conn.commit()
        return True
    except Exception as e:
        print(f"Migration failed: {str(e)}")
        return False
    finally:
        if conn:
            conn.close()

def wordpress_automation_task(config: dict) -> bool:
    """
    Example WordPress automation function
    Args:
        config: Dictionary containing WordPress configuration
    Returns:
        bool: True if automation succeeded
    """
    # Add your WordPress automation logic here
    # This might include:
    # - WordPress installation
    # - Plugin management
    # - Content updates
    return True
