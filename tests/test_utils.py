import pytest
import datetime
from datetime import date
from dateutil.tz import tzoffset
from pyticketswitch import utils
from pyticketswitch import exceptions


class TestDateRangeStr:

    def test_date_range_str(self):
        start_date = date(2016, 6, 21)
        end_date = date(2017, 1, 1)

        date_range_str = utils.date_range_str(start_date, end_date)
        assert date_range_str == '20160621:20170101'

    def test_date_range_str_with_datetimes(self):
        start_date = datetime.datetime(2016, 6, 21, 19, 30, 15)
        end_date = datetime.datetime(2017, 1, 1, 13, 45, 30)

        date_range_str = utils.date_range_str(start_date, end_date)
        assert date_range_str == '20160621:20170101'

    def test_date_range_str_with_no_end_date(self):
        start_date = date(2016, 6, 21)
        end_date = None

        date_range_str = utils.date_range_str(start_date, end_date)
        assert date_range_str == '20160621:'

    def test_date_range_str_with_no_start_date(self):
        start_date = None
        end_date = date(2017, 1, 1)

        date_range_str = utils.date_range_str(start_date, end_date)
        assert date_range_str == ':20170101'

    def test_date_range_str_with_no_start_date_or_end_date(self):
        start_date = None
        end_date = None

        date_range_str = utils.date_range_str(start_date, end_date)
        assert date_range_str == ''

    def test_date_range_str_with_invalid_end_date(self):
        start_date = date(2016, 6, 21)
        end_date = 'FOOBAR!'

        with pytest.raises(exceptions.InvalidParametersError):
            utils.date_range_str(start_date, end_date)

    def test_date_range_str_with_invalid_start_date(self):
        start_date = 'SAUSAGES!'
        end_date = date(2017, 1, 1)
        with pytest.raises(exceptions.InvalidParametersError):
            utils.date_range_str(start_date, end_date)


class TestIsoStrToDatetime:

    BST = tzoffset('BST', 3600)
    ZULU = tzoffset('ZULU', 0)

    def test_with_core_iso(self):
        date_str = '2016-09-16T19:30:00+01:00'
        dt = utils.isostr_to_datetime(date_str)

        assert dt == datetime.datetime(2016, 9, 16, 19, 30, 0, tzinfo=self.BST)

    def test_with_core_zulu(self):
        date_str = '2016-09-16T19:30:00Z'
        dt = utils.isostr_to_datetime(date_str)

        assert dt == datetime.datetime(2016, 9, 16, 19, 30, 0, tzinfo=self.ZULU)

    def test_with_python_iso(self):
        date_str = '2016-09-16T19:30:00+0100'
        dt = utils.isostr_to_datetime(date_str)

        assert dt == datetime.datetime(2016, 9, 16, 19, 30, 0, tzinfo=self.BST)

    def test_with_not_datetime(self):
        date_str = 'When the moon is in the forth corner of the jelly bean'
        with pytest.raises(ValueError):
            utils.isostr_to_datetime(date_str)

    def test_with_none(self):
        date_str = None
        with pytest.raises(ValueError):
            utils.isostr_to_datetime(date_str)

    def test_with_empty(self):
        date_str = ''
        with pytest.raises(ValueError):
            utils.isostr_to_datetime(date_str)


class TestYYYYToDate:

    def test_yyyymmdd_to_date_valid_string(self):
        date = utils.yyyymmdd_to_date('20160801')
        assert date.year == 2016
        assert date.month == 8
        assert date.day == 1

    def test_yyyymmdd_to_date_invalid_string(self):
        with pytest.raises(TypeError):
            utils.yyyymmdd_to_date(123)

        with pytest.raises(ValueError):
            utils.yyyymmdd_to_date('')

        with pytest.raises(ValueError):
            utils.yyyymmdd_to_date('wrong_date')


class TestSpecificDatesFromAPI:

    def test_specific_dates_from_api(self):
        api_data = {
            'year_2016': {
                'nov': {
                    'day_30': False,
                    'day_18': False,
                },
                'oct': {
                    'day_4': True,
                    'day_3': True,
                    'day_2': False,
                    'day_1': True,
                }
            }
        }
        results = utils.specific_dates_from_api_data(api_data)
        assert len(results) == 3
        assert type(results[0]) == datetime.date


class TestBitmaskToBooleanList:
    """
    NOTE: we are expecting big endian masks so the last bit of of our mask
    should the first element in our array
    """

    def test_simple_masks(self):
        # 0 == 0b0 so we only have one bit an it's a 0
        assert utils.bitmask_to_boolean_list(0) == [False]
        # 1 == 0b1 so we only have one bit an it's a 1
        assert utils.bitmask_to_boolean_list(1) == [True]
        # 5 == 0b101 so we expecting a length of 3 with the bits 1, 0 and 1
        assert utils.bitmask_to_boolean_list(5) == [True, False, True]
        # 6 == 0b110 so we expecting a length of 3 with the bits 0, 1 and 1
        assert utils.bitmask_to_boolean_list(6) == [False, True, True]


class TestBitmaskToNumberedList:

    def test_simple_masks(self):
        # 0 == 0b0 so we only have one bit an it's a 0
        assert utils.bitmask_to_numbered_list(0) == []
        # 1 == 0b1 so we only hanumberedbit an it's a 1
        assert utils.bitmask_to_numbered_list(1) == [1]
        # 5 == 0b101 so the 1st numbered bitst are 1's
        assert utils.bitmask_to_numbered_list(5) == [1, 3]
        # 6 == 0b110 so the 2nd numbered bits are 1's
        assert utils.bitmask_to_numbered_list(6) == [2, 3]