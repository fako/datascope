from datetime import datetime

import datagrowth.settings as datagrowth_settings


def parse_datetime_string(time_str):
    try:
        return datetime.strptime(time_str, datagrowth_settings.DATAGROWTH_DATETIME_FORMAT)
    except (ValueError, TypeError):
        return datetime(month=1, day=1, year=1970)


def format_datetime(datetime):
    return datetime.strftime(datagrowth_settings.DATAGROWTH_DATETIME_FORMAT)
