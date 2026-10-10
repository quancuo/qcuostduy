def total_minutes(days, minutes_per_day):
    return days * minutes_per_day


def minutes_to_hours(minutes):
    return minutes / 60


minutes = total_minutes(5, 40)
hours = minutes_to_hours(minutes)

print("Total minutes:", minutes)
print("Total hours:", hours)