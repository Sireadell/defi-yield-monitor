from src.db.session import get_db  # or however you create sessions
from src.spike_detector import detect_spikes, log_spikes

def main():
    with get_db() as db:
        spikes = detect_spikes(db)
        log_spikes(spikes)

if __name__ == "__main__":
    main()
