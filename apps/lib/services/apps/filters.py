from dateutil import parser

#"2024-11-28T15:37:15.249Z", 
def format_date(timestamp_firebase, format='%d/%m/%Y, %H:%M:%S'):
    dt = parser.parse(timestamp_firebase)
    return dt.strftime(format)