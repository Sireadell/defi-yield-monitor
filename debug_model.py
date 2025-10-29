# debug_model.py
import os, sys
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
SRC_DIR = os.path.join(SCRIPT_DIR, "src")
if SRC_DIR not in sys.path:
    sys.path.insert(0, SRC_DIR)

from src.db.models import PoolModel
from sqlalchemy import inspect

ins = inspect(PoolModel)
print("Columns in PoolModel:")
for col in ins.mapper.column_attrs:
    print(f"  • {col.key}")