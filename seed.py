import sqlite3
from datetime import datetime, timedelta

DB_PATH = "laundry.db"

def seed_database():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Drop tables entirely to guarantee zero duplicate or extra rows on re-run
    cursor.execute("DROP TABLE IF EXISTS runs")
    cursor.execute("DROP TABLE IF EXISTS machines")

    # Recreate tables with exact schema
    cursor.execute("""
        CREATE TABLE machines (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            kind TEXT,
            block TEXT,
            cycle_minutes INTEGER,
            in_service INTEGER
        )
    """)

    cursor.execute("""
        CREATE TABLE runs(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            machine_id INTEGER,
            roll_no TEXT,
            started_at DATETIME,
            ends_at DATETIME,
            collected_at DATETIME,
            status TEXT,
            FOREIGN KEY (machine_id) REFERENCES machines (id)
        )
    """)

    # 1. Insert exactly 8 Machines across blocks a, b, c, d (Machine 4 in Block B is out of service)
    machines_data = [
        ("Washer A1", "washer", "a", 30, 1),
        ("Dryer A1", "dryer", "a", 45, 1),
        ("Washer B1", "washer", "b", 30, 1),
        ("Dryer B1", "dryer", "b", 45, 0),  # Out of order
        ("Washer C1", "washer", "c", 30, 1),
        ("Dryer C1", "dryer", "c", 45, 1),
        ("Washer D1", "washer", "d", 30, 1),
        ("Dryer D1", "dryer", "d", 45, 1),
    ]
    cursor.executemany("""
        INSERT INTO machines (name, kind, block, cycle_minutes, in_service)
        VALUES (?, ?, ?, ?, ?)
    """, machines_data)

    now = datetime.now()
    yesterday = now - timedelta(days=1)
    fmt = "%Y-%m-%d %H:%M"

    # 2. Insert exactly 10 clean runs with roll numbers 1 through 10
    runs_data = [
        # --- Collected Runs (Yesterday & Today) ---
        (1, "1", yesterday.replace(hour=14, minute=0).strftime(fmt), yesterday.replace(hour=14, minute=30).strftime(fmt), yesterday.replace(hour=14, minute=45).strftime(fmt), "collected"),
        (2, "2", yesterday.replace(hour=15, minute=0).strftime(fmt), yesterday.replace(hour=15, minute=45).strftime(fmt), yesterday.replace(hour=16, minute=10).strftime(fmt), "collected"),
        (5, "3", yesterday.replace(hour=17, minute=30).strftime(fmt), yesterday.replace(hour=18, minute=0).strftime(fmt), yesterday.replace(hour=18, minute=15).strftime(fmt), "collected"),
        (6, "4", yesterday.replace(hour=19, minute=0).strftime(fmt), yesterday.replace(hour=19, minute=45).strftime(fmt), yesterday.replace(hour=20, minute=0).strftime(fmt), "collected"),
        (7, "6", (now - timedelta(hours=4)).strftime(fmt), (now - timedelta(hours=3, minutes=30)).strftime(fmt), (now - timedelta(hours=3, minutes=10)).strftime(fmt), "collected"),

        # --- Cleared Runs (Abandoned loads) ---
        (8, "5", yesterday.replace(hour=21, minute=0).strftime(fmt), yesterday.replace(hour=21, minute=45).strftime(fmt), None, "cleared"),
        (2, "7", (now - timedelta(hours=3)).strftime(fmt), (now - timedelta(hours=2, minutes=15)).strftime(fmt), None, "cleared"),

        # --- Active Running Runs (2 machines currently running) ---
        (1, "8", (now - timedelta(minutes=10)).strftime(fmt), (now + timedelta(minutes=20)).strftime(fmt), None, "running"),
        (3, "9", (now - timedelta(minutes=5)).strftime(fmt), (now + timedelta(minutes=1)).strftime(fmt), None, "running"),

        # --- Waiting for Pickup > 15 mins (1 machine waiting to be cleared) ---
        (6, "10", (now - timedelta(hours=1, minutes=15)).strftime(fmt), (now - timedelta(minutes=30)).strftime(fmt), None, "running"),
    ]

    cursor.executemany("""
        INSERT INTO runs (machine_id, roll_no, started_at, ends_at, collected_at, status)
        VALUES (?, ?, ?, ?, ?, ?)
    """, runs_data)

    conn.commit()
    conn.close()
    print("Database wiped and freshly seeded with exactly 8 machines and 10 runs!")

if __name__ == "__main__":
    seed_database()