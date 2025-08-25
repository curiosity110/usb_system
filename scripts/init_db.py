# scripts/init_db.py
import os, sys
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from app.db import engine
from app.models import Base

if __name__ == "__main__":
    Base.metadata.create_all(bind=engine)
    print("✅ DB tables created.")
