import json
import datetime
from ast import literal_eval

def utc_diff(zone):
    m = zone%100
    h = zone//100
    return h *3600 + m * 60

def date_format(date):
    arr = date.split()
    date = " ".join(arr[1:-1])
    zone = int(arr[-1])
    date_obj = datetime.datetime.strptime(date, '%d %b %Y %H:%M:%S')
    return date_obj, zone

def seconds_between(date1, date2):
    arr = []
    date1 = date1.replace("_"," ")
    date2 = date2.replace("_"," ")
    date_obj1, zone1 = date_format(date1)
    date_obj2, zone2 = date_format(date2)
    date_diff = int((date_obj1 - date_obj2).total_seconds())
    zone_diff = utc_diff(zone1) - utc_diff(zone2)
    arr.append(str(abs(date_diff - zone_diff)))
    
    return (json.dumps(arr))

