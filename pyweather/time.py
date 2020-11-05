from pendulum import now


def now_utc():
    """ Retrieve the current datetime in UTC

    Returns:
        (datetime): The current datetime in Universal Time, aka GMT
    """
    return now()


def month_to_int(month):
    if isinstance(month, int) or isinstance(month, float):
        return int(month)
    if isinstance(month, str):
        month = month.lower()
        if month.startswith("jan"):
            return 1
        if month.startswith("feb"):
            return 2
        if month.startswith("mar"):
            return 3
        if month.startswith("apr"):
            return 4
        if month.startswith("may"):
            return 5
        if month.startswith("jun"):
            return 6
        if month.startswith("jul"):
            return 7
        if month.startswith("aug"):
            return 8
        if month.startswith("sep"):
            return 9
        if month.startswith("oct"):
            return 10
        if month.startswith("nov"):
            return 11
        if month.startswith("dec"):
            return 12
    return None


def weekday_to_int(weekday):
    if isinstance(weekday, int) or isinstance(weekday, float):
        return int(weekday)
    if isinstance(weekday, str):
        weekday = weekday.lower()
        if weekday.startswith("mon"):
            return 0
        if weekday.startswith("tue"):
            return 1
        if weekday.startswith("wed"):
            return 2
        if weekday.startswith("thu"):
            return 3
        if weekday.startswith("fri"):
            return 4
        if weekday.startswith("sat"):
            return 5
        if weekday.startswith("sun"):
            return 6
    return None


def int_to_month(month):
    if month == 1:
        return "january"
    if month == 2:
        return "february"
    if month == 3:
        return "march"
    if month == 4:
        return "april"
    if month == 5:
        return "may"
    if month == 6:
        return "june"
    if month == 7:
        return "july"
    if month == 8:
        return "august"
    if month == 9:
        return "september"
    if month == 10:
        return "october"
    if month == 11:
        return "november"
    if month == 12:
        return "december"
    return str(month)


def int_to_weekday(weekday):
    if weekday == 0:
        return "monday"
    if weekday == 1:
        return "tuesday"
    if weekday == 2:
        return "wednesday"
    if weekday == 3:
        return "thursday"
    if weekday == 4:
        return "friday"
    if weekday == 5:
        return "saturday"
    if weekday == 6:
        return "sunday"
    return str(weekday)


def in_utc(date):
    return date.in_timezone("UTC")
