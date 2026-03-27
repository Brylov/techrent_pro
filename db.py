from datetime import datetime

class Equipment:
    def __init__(self, id: int, name: str, category: str, daily_rate: float, quantity: int, description: str, available: bool):
        self._id: int = id
        self._name: str = name
        self._category: str = category
        self._daily_rate: float = daily_rate
        self._quantity: int = quantity
        self._description: str = description
        self._available: bool = available

class Customer:
    def __init__(self, id: int, name: str, email: str, phone: str, created_at: str ):
        self._id: int = id
        self._name: str = name
        self._email: str = email
        self._phone: str = phone
        # Validation: Ensure the string is in ISO format (YYYY-MM-DD)
        try:
            # This converts the string to a date object to "test" it
            # then stores it back as an ISO formatted string.
            self._created_at: str = datetime.fromisoformat(created_at).isoformat()
        except ValueError:
            raise ValueError(f"Invalid date format for '{created_at}'. Expected ISO format (YYYY-MM-DD).")


from enum import Enum

class STATUS(Enum):
    ACTIVE = 1
    RETURNED = 1
    OVERDUE = 1
    
class Rental:
    def __init__(self, id: int, equipment_id: int, customer_id: int, start_date: str, end_date: str, status: STATUS, total_cost: float):
        self._id: int = id
        self._equipment_id: int = equipment_id
        self._customer_id: int = customer_id
        self._start_date: str = start_date
        self._end_date: str = end_date
        self._status: STATUS = status
        self._total_cost: float = total_cost


equipment_data = [
    {"id": 101, "name": "Sony A7IV Camera", "category": "Photography", "daily_rate": 150.0, "quantity": 5, "description": "Full-frame mirrorless camera", "available": True},
    {"id": 102, "name": "DJI Ronin RS3", "category": "Gimbal", "daily_rate": 45.0, "quantity": 3, "description": "3-axis camera stabilizer", "available": True},
    {"id": 103, "name": "Aputure 600d Pro", "category": "Lighting", "daily_rate": 85.0, "quantity": 2, "description": "High-output LED daylight lamp", "available": False},
    {"id": 104, "name": "Sennheiser MKH 416", "category": "Audio", "daily_rate": 35.0, "quantity": 4, "description": "Short shotgun interference tube microphone", "available": True},
    {"id": 105, "name": "SmallHD 702 Touch", "category": "Monitor", "daily_rate": 40.0, "quantity": 6, "description": "7-inch high-bright field monitor", "available": True},
    {"id": 106, "name": "Teradek Bolt 6", "category": "Wireless", "daily_rate": 120.0, "quantity": 2, "description": "4K zero-delay wireless video system", "available": False}
]

customer_data = [
    {"id": 1, "name": "Alex Rivera", "email": "arivera@indie-film.com", "phone": "555-0101", "created_at": "2024-01-15"},
    {"id": 2, "name": "Sarah Chen", "email": "schen_photo@gmail.com", "phone": "555-0102", "created_at": "2024-02-20"},
    {"id": 3, "name": "Marcus Thorne", "email": "m.thorne@globalmedia.net", "phone": "555-0103", "created_at": "2024-03-05"},
    {"id": 4, "name": "Elena Vance", "email": "evance@blackmesa.org", "phone": "555-0104", "created_at": "2024-05-12"},
]

rental_data = [
    {"id": 5001, "equipment_id": 101, "customer_id": 2, "start_date": "2026-03-20", "end_date": "2026-03-23", "status": 2, "total_cost": 450.0},
    {"id": 5002, "equipment_id": 103, "customer_id": 1, "start_date": "2026-03-25", "end_date": "2026-03-28", "status": 1, "total_cost": 255.0},
    {"id": 5003, "equipment_id": 106, "customer_id": 3, "start_date": "2026-03-26", "end_date": "2026-03-30", "status": 1, "total_cost": 480.0},
]

if __name__ == "__main__":
    #print(Equipment(1,"a","a",3.13,1,"a",True))
    pass
    