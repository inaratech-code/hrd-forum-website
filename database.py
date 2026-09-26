"""
database.py - Legacy Database Module (Deprecated)

Database operations have been unified under Django's ORM schema and migrations (main_app/models.py).
Raw SQLite table initialization is disabled to prevent dual-table conflicts.
"""
import os
import hashlib
import warnings

def get_db_path():
    """Returns the fallback SQLite database path for local development."""
    if os.environ.get('VERCEL') or not os.access(os.path.dirname(__file__), os.W_OK):
        return '/tmp/hrd_forum.db'
    return os.path.join(os.path.dirname(__file__), 'hrd_forum.db')

def hash_password(password):
    """SHA-256 password hashing utility."""
    return hashlib.sha256(password.encode('utf-8')).hexdigest()

def init_db():
    """
    Deprecated: Database initialization is managed via Django migrations.
    Run `python manage.py migrate` for database schema updates.
    """
    warnings.warn(
        "database.init_db() is deprecated. All database models are managed via Django ORM (main_app/models.py).",
        DeprecationWarning,
        stacklevel=2
    )

if __name__ == '__main__':
    print("Database management is unified under Django ORM. Use 'python manage.py migrate'.")
