import traceback
import importlib
from datetime import datetime
from sqlalchemy import inspect
from sqlalchemy.exc import SQLAlchemyError

print("\n=== 🔍 Full Runtime Diagnostic: DeFi Yield Monitor ===\n")

results = []
errors = []

def safe_test(name, func):
    """Run each test safely and log errors without stopping."""
    try:
        func()
        results.append((name, "✅ PASS"))
    except Exception as e:
        tb = traceback.format_exc()
        results.append((name, "❌ FAIL"))
        errors.append((name, str(e), tb))

# === 1. Test imports ===
def test_imports():
    modules = [
        "src.config",
        "src.db.base",
        "src.db.models",
        "src.db.session",
        "src.db.crud",
        "src.data.fetcher",
        "src.data.detector",
        "src.spike_detector",
    ]
    for m in modules:
        importlib.import_module(m)

safe_test("Module imports", test_imports)

# === 2. Test database engine + Base ===
def test_db_engine():
    from src.db.session import engine
    from src.db.base import Base
    inspector = inspect(engine)
    print(f"Connected DB: {engine.url}")
    print("Existing tables:", inspector.get_table_names())

safe_test("Database connection & schema check", test_db_engine)

# === 3. Test table creation ===
def test_create_tables():
    from src.db.base import Base
    from src.db.session import engine
    Base.metadata.create_all(bind=engine)
    inspector = inspect(engine)
    if not inspector.get_table_names():
        raise RuntimeError("No tables found after create_all()")

safe_test("Create tables", test_create_tables)
# === 4. Test DB session ===
def test_db_session():
    from src.db.session import get_db
    from sqlalchemy import text

    with get_db() as db:
        db.execute(text("SELECT 1"))

safe_test("Database session generator", test_db_session)

# === 5. Test fetcher ===
def test_fetcher():
    from src.data.fetcher import fetch_sample_pool
    pool = fetch_sample_pool()
    assert pool.protocol and pool.chain
    print(f"Fetched sample pool: {pool.protocol} ({pool.chain})")

safe_test("Fetcher logic", test_fetcher)

# === 6. Test spike detector ===
def test_spike_detector():
    from src.data.detector import detect_spike
    from src.db.models import PoolModel
    from datetime import datetime

    old = PoolModel(pool_id="1", protocol="Test", chain="Somnia", apy=0.1, tvl=100, last_updated=datetime.utcnow())
    new = PoolModel(pool_id="1", protocol="Test", chain="Somnia", apy=0.2, tvl=140, last_updated=datetime.utcnow())

    result = detect_spike(old, new)
    print("Spike detection result:", result)
    assert isinstance(result, dict)

safe_test("Spike detector logic", test_spike_detector)

# === 7. Test full system ===
def test_full_integration():
    from src.spike_detector import detect_spikes
    from src.db.session import SessionLocal
    db = SessionLocal()
    detect_spikes(db)
    db.close()

safe_test("Full spike detection integration", test_full_integration)

# === Summary ===
print("\n--- SUMMARY ---")
for name, status in results:
    print(f"{status:<10} {name}")

if errors:
    print("\n--- ERRORS FOUND ---")
    for name, err, tb in errors:
        print(f"\n❌ {name}: {err}\n{tb}")
else:
    print("\n🎉 All systems operational — no errors found!")

print(f"\nReport generated at {datetime.utcnow()} UTC\n")
