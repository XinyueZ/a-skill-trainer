from datetime import datetime
from zoneinfo import ZoneInfo


def get_current_local_datetime():
    berlin_tz = ZoneInfo("Europe/Berlin")
    now_de = datetime.now(berlin_tz)

    formatted_time = now_de.strftime("%d.%m.%Y %H:%M:%S")
    return formatted_time
