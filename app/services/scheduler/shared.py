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
) -> list[DailyAvailability]: #used as hint for programmers/code reviewers to tell, what is this function's gonna return, it will return a list , with daily availabbility object
    window = []
    for i in range(num_days):
        day = start + timedelta(days=i) #to add the days in the loop, we use timedelta function, which is just used to add the dates with number of days

        #weekday function represents 0 - monday, 1 - tuesday, ....and so on..., 5 - saturday, 6 - sunday
        if day.weekday() >= 5:
            hours = weekend_hours 
        else:
            hours = weekday_hours
        window.append(DailyAvailability(day=day, available_hours=hours)) #this appends the object at the end of the window list, the class we created above, daily available, creating its one instance which takes date of the day, and allocates hours for that day
    return window
