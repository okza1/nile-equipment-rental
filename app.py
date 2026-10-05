from nile_app.config import COMPANY_NAME
from nile_app.storage import initialize_database, export_backup
from nile_app.services import (
    get_all_equipment,
    get_all_creators,
    get_all_bookings,
    create_booking,
    verify_and_release,
    get_booking_by_id,
    get_equipment_by_id,
    calculate_nile_fees,
)


def format_money(value: float) -> str:
    return f"R{value:,.2f}"


def show_equipment(equipment=None):
    data = equipment if equipment is not None else get_all_equipment()
    print("\n" + "=" * 75)
    for item in data:
        status = "✅ AVAILABLE" if item["available"] else "🔴 BOOKED"
        print(
            f"ID:{item['id']} | {item['name']} | {format_money(item['price'])}/day | "
            f"{item['location']} | {status}"
        )


def show_bookings():
    print("\n=== NILE BOOKINGS ===")
    bookings = get_all_bookings()
    if not bookings:
        print("No bookings found.")
        return

    for booking in bookings:
        print(f"\n{booking['booking_id']} | {booking['equipment_name']} | Status: {booking['status']}")
        print(f"  Total Escrow Hold: {format_money(booking['fees']['total_contractor_pays'])} | Owner Payout: {format_money(booking['fees']['owner_receives'])}")
        if booking.get("verification_photo"):
            print(f"  📸 Proof: {booking['verification_photo']} by {booking['verified_by']}")


def book_equipment():
    show_equipment()
    try:
        equipment_id = int(input("\nID to book: ").strip())
    except ValueError:
        print("Invalid equipment ID.")
        return

    try:
        days = int(input("Days?: ").strip())
    except ValueError:
        days = 1

    use_inspection = input("Add Creator Inspection R490? (y/n): ").strip().lower() == "y"

    try:
        booking = create_booking(equipment_id=equipment_id, days=days, inspection_required=use_inspection)
    except ValueError as exc:
        print(f"Booking failed: {exc}")
        return

    fees = booking["fees"]
    print(f"\nTOTAL in Escrow: {format_money(fees['total_contractor_pays'])} | Owner gets: {format_money(fees['owner_receives'])}")
    confirm = input("Confirm hold in Escrow? (y/n): ").strip().lower()
    if confirm != "y":
        print("Booking cancelled.")
        return

    saved_booking = create_booking(equipment_id=equipment_id, days=days, inspection_required=use_inspection, confirm=True)
    print(f"\n🎉 BOOKED! {saved_booking['booking_id']} is now ESCROW_HELD")


def verify_and_release_flow():
    show_bookings()
    bookings = get_all_bookings()
    if not bookings:
        return

    booking_id = input("\nEnter Booking ID to verify: ").strip().upper()
    booking = get_booking_by_id(booking_id)
    if not booking:
        print("Booking not found")
        return
    if booking["status"] == "RELEASED":
        print("Already released!")
        return

    creators = get_all_creators()
    print("\n--- CREATOR VERIFICATION ---")
    for creator in creators:
        print(f"  ID:{creator['id']} | {creator['name']} - {creator['service']}")

    try:
        creator_id = int(input("Which Creator verified? Enter ID: ").strip())
    except ValueError:
        print("Invalid creator ID")
        return

    photo_proof = input("Enter photo proof path OR type 'photo_taken': ").strip()
    if not photo_proof:
        photo_proof = f"site_proof_{booking_id}.jpg"

    try:
        released_booking = verify_and_release(
            booking_id=booking_id,
            creator_id=creator_id,
            photo_proof=photo_proof,
        )
    except ValueError as exc:
        print(f"Verification failed: {exc}")
        return

    machine = get_equipment_by_id(released_booking["equipment_id"])
    print(f"\n🔍 Verifying {photo_proof} by {released_booking['verified_by']}...")
    print("✅ Photo verified! Site clean, machine inspected.")
    print("\n" + "=" * 60)
    print("💸 ESCROW RELEASED SUCCESSFULLY!")
    print(f"Booking ID:     {released_booking['booking_id']}")
    print(f"Owner Payout:   {format_money(released_booking['fees']['owner_receives'])}")
    print(f"Creator Payout: {format_money(released_booking['fees']['creator_payout'])} -> {released_booking['verified_by']}")
    print(f"Nile Net Share: {format_money(released_booking['fees']['nile_total_revenue'])}")
    if machine:
        print(f"Equipment '{machine['name']}' status set to AVAILABLE")
    print("=" * 60)


def main():
    initialize_database()
    export_backup(force=False)

    while True:
        print(f"""
========== {COMPANY_NAME} - V3.1 ==========
1. View Equipment Catalog
2. Book Equipment (Hold Escrow)
3. View All Bookings
4. 📸 Creator Verify & Release Escrow
5. Export Data Backup
6. Exit
===========================================""")
        choice = input("Select Option (1-6): ").strip()

        if choice == "1":
            show_equipment()
        elif choice == "2":
            book_equipment()
        elif choice == "3":
            show_bookings()
        elif choice == "4":
            verify_and_release_flow()
        elif choice == "5":
            export_backup(force=True)
        elif choice == "6":
            export_backup(force=True)
            print("Session saved. System ready for deployment.")
            break
        else:
            print("Invalid selection.")


if __name__ == "__main__":
    main()
    

















































































































































""""""""""""""
