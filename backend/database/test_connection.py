import sys
from sqlalchemy import create_engine, text
from backend.config import settings

def test_connection():
    print(f"Testing database connection to: {settings.DATABASE_URL.split('@')[-1]}...")
    try:
        engine = create_engine(settings.DATABASE_URL)
        with engine.connect() as connection:
            result = connection.execute(text("SELECT 1"))
            val = result.scalar()
            if val == 1:
                print("Database connection successfully established!")
                return True
            else:
                print(f"Database returned unexpected value: {val}")
                return False
    except Exception as e:
        print(f"Database connection failed: {e}", file=sys.stderr)
        return False

if __name__ == "__main__":
    success = test_connection()
    sys.exit(0 if success else 1)
