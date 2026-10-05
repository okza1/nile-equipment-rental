import json
import random
from datetime import datetime

from nile_app.config import (
    COMPANY_NAME,
    INSPECTION_FEE,
    NILE_COMMISSION,
    OWNER_PROTECTION_CONTRIBUTION,
    PROTECTION_FEE,
)
from nile_app.storage import export_backup, get_connection, initialize_database, load_backup


def calculate_nile_fees(daily_price, days=1, with_inspection=True):
    subtotal = daily_price * days
    nile_cut = subtotal * NILE_COMMISSION
    inspection = INSPECTION_FEE if with_inspection else 0
    creator_payout = INSPECTION_FEE * 0.80 if with_inspection else 0
    nile_inspection_margin = inspection - creator_payout

    total_to_contractor = subtotal + PROTECTION_FEE + inspection
    owner_payout = max(0, subtotal - nile_cut - OWNER_PROTECTION_CONTRIBUTION)
    total_nile_revenue = nile_cut + PROTECTION_FEE + OWNER_PROTECTION_CONTRIBUTION + nile_inspection_margin

    return {
        "subtotal": subtotal,
        "nile_commission": nile_cut,
        "protection_fee": PROTECTION_FEE,
        "inspection_fee": inspection,
        "creator_payout": creator_payout,
        "total_contractor_pays": total_to_contractor,
        "owner_receives": owner_payout,
        "nile_total_revenue": total_nile_revenue,
    }


def generate_booking_id(prefix="NIL"):
    return f"{prefix}-{random.randint(10000, 99999)}"


def get_all_equipment():
    conn = get_connection()
    rows = conn.execute("SELECT * FROM equipment ORDER BY id").fetchall()
    conn.close()
    return [dict(row) for row in rows]


def get_all_creators():
    conn = get_connection()
    rows = conn.execute("SELECT * FROM creators ORDER BY id").fetchall()
    conn.close()
    return [dict(row) for row in rows]


def get_all_bookings():
    conn = get_connection()
    rows = conn.execute("SELECT * FROM bookings ORDER BY date DESC").fetchall()
    conn.close()
    return [
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
        for row in rows
    ]


def get_equipment_by_id(equipment_id):
    conn = get_connection()
    row = conn.execute("SELECT * FROM equipment WHERE id = ?", (equipment_id,)).fetchone()
    conn.close()
    if not row:
        return None
    return dict(row)


def get_creator_by_id(creator_id):
    conn = get_connection()
    row = conn.execute("SELECT * FROM creators WHERE id = ?", (creator_id,)).fetchone()
    conn.close()
    if not row:
        return None
    return dict(row)


def get_booking_by_id(booking_id):
    conn = get_connection()
    row = conn.execute("SELECT * FROM bookings WHERE booking_id = ?", (booking_id,)).fetchone()
    conn.close()
    if not row:
        return None
    return {
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


def create_booking(equipment_id, days, inspection_required=True, confirm=False):
    if days <= 0:
        raise ValueError("Booking days must be greater than zero.")

    equipment = get_equipment_by_id(equipment_id)
    if not equipment:
        raise ValueError("Equipment not found.")
    if not equipment["available"]:
        raise ValueError("Equipment is not currently available.")

    fees = calculate_nile_fees(equipment["price"], days, inspection_required)
    booking_id = generate_booking_id()

    if not confirm:
        return {
            "booking_id": booking_id,
            "equipment_id": equipment_id,
            "equipment_name": equipment["name"],
            "days": days,
            "fees": fees,
            "status": "DRAFT",
        }

    conn = get_connection()
    conn.execute(
        "INSERT INTO bookings (booking_id, equipment_id, equipment_name, days, fees, date, status) VALUES (?, ?, ?, ?, ?, ?, ?)",
        (
            booking_id,
            equipment_id,
            equipment["name"],
            days,
            json.dumps(fees),
            str(datetime.now()),
            "ESCROW_HELD",
        ),
    )
    conn.execute(
        "UPDATE equipment SET available = 0 WHERE id = ?",
        (equipment_id,),
    )
    conn.commit()
    conn.close()

    export_backup(force=True)
    return get_booking_by_id(booking_id)


def verify_and_release(booking_id, creator_id, photo_proof):
    booking = get_booking_by_id(booking_id)
    if not booking:
        raise ValueError("Booking not found")
    if booking["status"] == "RELEASED":
        raise ValueError("Already released")

    creator = get_creator_by_id(creator_id)
    if not creator:
        raise ValueError("Creator not found")

    conn = get_connection()
    conn.execute(
        "UPDATE bookings SET verification_photo = ?, verified_by = ?, status = 'RELEASED', release_date = ? WHERE booking_id = ?",
        (photo_proof, creator["name"], str(datetime.now()), booking_id),
    )
    conn.execute(
        "UPDATE equipment SET available = 1 WHERE id = ?",
        (booking["equipment_id"],),
    )
    conn.commit()
    conn.close()

    updated_booking = get_booking_by_id(booking_id)
    export_backup(force=True)
    return updated_booking


def initialize_app():
    initialize_database()
    export_backup(force=False)
