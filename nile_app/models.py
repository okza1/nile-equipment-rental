from dataclasses import dataclass
from typing import Optional


@dataclass
class Equipment:
    id: int
    name: str
    type: str
    price: float
    location: str
    owner: str
    verified: bool = True
    available: bool = True

    @classmethod
    def from_row(cls, row):
        return cls(
            id=row[0],
            name=row[1],
            type=row[2],
            price=float(row[3]),
            location=row[4],
            owner=row[5],
            verified=bool(row[6]),
            available=bool(row[7]),
        )


@dataclass
class Creator:
    id: int
    name: str
    service: str
    price: float
    location: str

    @classmethod
    def from_row(cls, row):
        return cls(
            id=row[0],
            name=row[1],
            service=row[2],
            price=float(row[3]),
            location=row[4],
        )


@dataclass
class Booking:
    booking_id: str
    equipment_id: int
    equipment_name: str
    days: int
    fees: dict
    date: str
    status: str = "ESCROW_HELD"
    verification_photo: Optional[str] = None
    verified_by: Optional[str] = None
    release_date: Optional[str] = None

    @classmethod
    def from_row(cls, row):
        return cls(
            booking_id=row[0],
            equipment_id=row[1],
            equipment_name=row[2],
            days=row[3],
            fees=row[4],
            date=row[5],
            status=row[6],
            verification_photo=row[7],
            verified_by=row[8],
            release_date=row[9],
        )
