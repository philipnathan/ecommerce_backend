from datetime import datetime
import pytz


def change_date(data, timezone):
    try:
        if timezone is None:
            raise ValueError("Please provide timezone")

        local_time = datetime.strptime(data, "%Y-%m-%d %H:%M:%S")

        local_tz = pytz.timezone(timezone)
        local_time = local_tz.localize(local_time, False)

        utc_time = local_time.astimezone(pytz.utc)

        return utc_time
    except (Exception, ValueError) as e:
        raise e
