from datetime import date
from dateutil import parser
from pyticketswitch.exceptions import InvalidParametersError


def date_range_str(start_date, end_date):
    if start_date and not isinstance(start_date, date):
        raise InvalidParametersError("start_date is not a datetime instance")
    if end_date and not isinstance(end_date, date):
        raise InvalidParametersError("end_date is not a datetime instance")

    if start_date:
        start_date = start_date.strftime('%Y%m%d')
    else:
        start_date = ''

    if end_date:
        end_date = end_date.strftime('%Y%m%d')
    else:
        end_date = ''

    if start_date or end_date:
        date_range = '{}:{}'.format(start_date, end_date)
    else:
        date_range = ''

    return date_range


def isostr_to_datetime(date_str):
    if not date_str:
        raise ValueError('{} is not a valid datetime string'.format(date_str))

    dt = parser.parse(date_str)
    return dt
