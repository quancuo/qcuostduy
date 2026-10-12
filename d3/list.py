minutes  = [20,45,30,45,60,15]

def filter_minutes(minute,minimum):
    selected = []

    for x in minutes:
        if x >= minimum:
            selected.append(x)
    return selected

print(filter_minutes(minutes, 30))
print(filter_minutes(minutes, 45))
print(filter_minutes(minutes, 60))


