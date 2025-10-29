import importlib
import logging
import traceback

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

TESTS = [
    ("Import config", lambda: importlib.import_module("src.config")),
    ("Import DB models", lambda: importlib.import_module("src.db.models")),
    ("Import DB CRUD", lambda: importlib.import_module("src.db.crud")),
    ("Import DB base", lambda: importlib.import_module("src.db.base")),
    ("Import fetcher", lambda: importlib.import_module("src.data.fetcher")),
    ("Import detector", lambda: importlib.import_module("src.data.detector")),
    ("Database connection", lambda: importlib.import_module("src.db.session")),
    ("Run sample fetcher", lambda: importlib.import_module("src.test_fetcher")),
]

def run_test(name, func):
    try:
        func()
        logging.info(f"✅ {name}: PASSED")
        return True
    except Exception as e:
        logging.error(f"❌ {name}: FAILED - {e}")
        traceback.print_exc()
        return False

if __name__ == "__main__":
    logging.info("Starting full system test...\n")
    results = [run_test(name, func) for name, func in TESTS]

    passed = sum(results)
    failed = len(results) - passed
    logging.info("\n--- SUMMARY ---")
    logging.info(f"Total Tests: {len(TESTS)}")
    logging.info(f"✅ Passed: {passed}")
    logging.info(f"❌ Failed: {failed}")

    if failed == 0:
        logging.info("\n🎉 All systems operational!")
    else:
        logging.warning("\n⚠️ Some modules failed. Fix above errors before running detector.")
