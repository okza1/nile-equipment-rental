import json
import os
import sqlite3
from datetime import datetime

from nile_app.config import DB_PATH, BACKUP_PATH


def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def initialize_database():
    conn = get_connection()
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS equipment (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            type TEXT NOT NULL,
            price REAL NOT NULL,
            location TEXT NOT NULL,
            owner TEXT NOT NULL,
            verified INTEGER NOT NULL DEFAULT 1,
            available INTEGER NOT NULL DEFAULT 1
        )
        """
    )
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS creators (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            service TEXT NOT NULL,
            price REAL NOT NULL,
            location TEXT NOT NULL
        )
        """
    )
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS bookings (
            booking_id TEXT PRIMARY KEY,
            equipment_id INTEGER NOT NULL,
            equipment_name TEXT NOT NULL,
            days INTEGER NOT NULL,
            fees TEXT NOT NULL,
            date TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'ESCROW_HELD',
            verification_photo TEXT,
            verified_by TEXT,
            release_date TEXT
        )
        """
    )

    equipment_seed = [
        (1, "Bobcat Mini Excavator", "Mini Excavator", 1200, "Johannesburg", "Thabo M.", 1, 1),
        (2, "JCB 3T Mini Excavator", "Mini Excavator", 1450, "Pretoria", "Mokoena Plant", 1, 1),
        (3, "Skid Steer Loader", "Skid Steer", 1100, "Midrand", "Khumalo Equipment", 1, 1),
        (4, "Compact Site Loader", "Site Loader", 900, "Soweto", "Nile Fleet Partner", 1, 1),
    ]

    creators_seed = [
        (1, "Lebo Visuals", "Site Inspection", 490, "Johannesburg"),
        (2, "Gauteng Drone Works", "Drone Site Video", 650, "Pretoria"),
    ]

    existing_equipment = conn.execute("SELECT COUNT(*) FROM equipment").fetchone()[0]
    if existing_equipment == 0:
        conn.executemany(
            "INSERT INTO equipment (id, name, type, price, location, owner, verified, available) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            equipment_seed,
        )

    existing_creators = conn.execute("SELECT COUNT(*) FROM creators").fetchone()[0]
    if existing_creators == 0:
        conn.executemany(
            "INSERT INTO creators (id, name, service, price, location) VALUES (?, ?, ?, ?, ?)",
            creators_seed,
        )

    conn.commit()
    conn.close()


def export_backup(force: bool = False):
    if os.path.exists(BACKUP_PATH) and not force:
        return BACKUP_PATH

    conn = get_connection()
    equipment_rows = conn.execute("SELECT * FROM equipment").fetchall()
    booking_rows = conn.execute("SELECT * FROM bookings").fetchall()
    conn.close()

    data = {
        "equipment": [dict(row) for row in equipment_rows],
        "bookings": [
            {
                "booking_id": row["booking_id"],
                "equipment_id": row["equipment_id"],
                "equipment_name": row["equipment_name"],
                "days": row["days"],
                "fees": json.loads(row["fees"]),
                "date": row["date"],
                "status": row["status"],
                "verification_photo": row["verification_photo"],
                "verified_by": row["verified_by"],
                "release_date": row["release_date"],
            }
            for row in booking_rows
        ],
        "last_save": str(datetime.now()),
    }

    with open(BACKUP_PATH, "w") as fh:
        json.dump(data, fh, indent=2)

    return BACKUP_PATH


def load_backup():
    if not os.path.exists(BACKUP_PATH):
        return

    with open(BACKUP_PATH, "r") as fh:
        data = json.load(fh)

    if "equipment" in data:
        conn = get_connection()
        conn.execute("DELETE FROM equipment")
        conn.executemany(
            "INSERT INTO equipment (id, name, type, price, location, owner, verified, available) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            [
                (
                    item["id"],
                    item["name"],
                    item["type"],
                    item["price"],
                    item["location"],
                    item["owner"],
                    int(item.get("verified", True)),
                    int(item.get("available", True)),
                )
                for item in data["equipment"]
            ],
        )
        conn.commit()
        conn.close()

    if "bookings" in data:
        conn = get_connection()
        conn.execute("DELETE FROM bookings")
        conn.executemany(
            "INSERT INTO bookings (booking_id, equipment_id, equipment_name, days, fees, date, status, verification_photo, verified_by, release_date) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            [
                (
                    booking["booking_id"],
                    booking["equipment_id"],
                    booking["equipment_name"],
                    booking["days"],
                    json.dumps(booking["fees"]),
                    booking["date"],
                    booking["status"],
                    booking.get("verification_photo"),
                    booking.get("verified_by"),
                    booking.get("release_date"),
                )
                for booking in data["bookings"]
            ],
        )
        conn.commit()
        conn.close()
