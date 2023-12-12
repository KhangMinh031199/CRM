from datetime import datetime, timedelta

import time
import arrow
from pytz import timezone
import pandas as pd
from_date = '14-06-2022 23:59:00+07:00'

from_obj = datetime.strptime(from_date, '%d-%m-%Y %H:%M:%S%z')+ timedelta(hours=-7)
print (from_obj)
from_tmp = time.mktime(from_obj.timetuple()) 
print (from_tmp)


test_timestamp = '1655251076.15841'

print (float(from_tmp) > float(test_timestamp))


def tz_diff(date, tz1, tz2):
    '''
    Returns the difference in hours between timezone1 and timezone2
    for a given date.
    '''
    date = pd.to_datetime(date)
    return (tz1.localize(date) - 
            tz2.localize(date).astimezone(tz1))\
            .seconds/3600


print(arrow.get(float(test_timestamp)).tzinfo)
print(arrow.get(float(test_timestamp)).to('Asia/Ho_Chi_Minh').format('YYYY-MM-DD HH:mm:ss'))


utc = timezone('UTC')
aus = timezone('Asia/Ho_Chi_Minh')

print(tz_diff('2017-01-01', utc, aus))