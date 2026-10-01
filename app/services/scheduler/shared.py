from dataclasses import dataclass
from datetime import date, timedelta


#Building/Defining two data classes to be used in OR_TOOLs so the object can be made immediately

@dataclass
class ScheduledBlock:
    topic_id: int
    topic_name: str
    scheduled_date: date
    duration_minutes: int

#print(ScheduledBlock(1,"DDA Algorithm", 3/10/2026,90))

@dataclass
class DailyAvailability:
    day: date
    available_hours: float

#print(DailyAvailability()) ignore this one


def build_availability_window(
    start: date, num_days: int, weekday_hours: float, weekend_hours: float
) -> list[DailyAvailability]:
    window = []
    for i in range(num_days):
        day = start + timedelta(days=i)


        hours = weekend_hours if day.weekday() >= 5 else weekday_hours
        window.append(DailyAvailability(day=day, available_hours=hours))
    return window