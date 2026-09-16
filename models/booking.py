import uuid
from dataclasses import asdict, dataclass, field
from typing import Any


@dataclass
class BookingDates:
    checkin: str
    checkout: str


@dataclass
class Booking:
    firstname: str
    lastname: str
    totalprice: int
    depositpaid: bool
    bookingdates: BookingDates
    additionalneeds: str = ""
    extra_fields: dict[str, Any] = field(default_factory=dict, repr=False)

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload.pop("extra_fields", None)
        payload.update(self.extra_fields)
        return payload

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Booking":

        dates = data.get("bookingdates") or {}
        known = {
            "firstname",
            "lastname",
            "totalprice",
            "depositpaid",
            "bookingdates",
            "additionalneeds",
        }
        extra = {key: value for key, value in data.items() if key not in known}
        
        return cls(
            firstname=data["firstname"],
            lastname=data["lastname"],
            totalprice=int(data["totalprice"]),
            depositpaid=bool(data["depositpaid"]),
            bookingdates=BookingDates(checkin=dates["checkin"], checkout=dates["checkout"]),
            additionalneeds=data.get("additionalneeds", ""),
            extra_fields=extra,
        )

    @classmethod
    def from_template(cls, template: dict[str, Any], unique = True) -> "Booking":
        """读取 data/booking.json 后生成一条数据；unique=True 时给姓名加后缀，避免和其他测试撞数据。"""
        booking = cls.from_dict(template)
        if unique:
            suffix = uuid.uuid4().hex[:8]
            booking.firstname = f"{booking.firstname}{suffix}"
            booking.lastname = f"{booking.lastname}{suffix}"
        return booking
