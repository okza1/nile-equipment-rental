import json

from nile_app.services import calculate_nile_fees, create_booking, get_all_equipment, get_all_creators
from nile_app.storage import get_connection, initialize_database


def test_fee_calculation():
    result = calculate_nile_fees(1200, 3, True)
    assert result["subtotal"] == 3600
    assert result["inspection_fee"] == 490
    assert result["creator_payout"] == 392.0
    assert result["total_contractor_pays"] == 3600 + 250 + 490
    assert result["owner_receives"] >= 0


def test_create_booking_requires_valid_equipment():
    initialize_database()
    try:
        create_booking(9999, 2, True, confirm=False)
        assert False, "Expected ValueError for invalid equipment"
    except ValueError:
        pass


def test_seed_data_exists():
    initialize_database()
    equipment = get_all_equipment()
    creators = get_all_creators()
    assert len(equipment) >= 4
    assert len(creators) >= 2


def test_db_has_expected_tables():
    initialize_database()
    conn = get_connection()
    tables = conn.execute(
        "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"
    ).fetchall()
    conn.close()
    names = {row[0] for row in tables}
    assert {"equipment", "creators", "bookings"}.issubset(names)
