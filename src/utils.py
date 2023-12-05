import datetime 
import glob
from typing import Optional, Tuple

def getDatetimePrettyFormat() -> str:
    return datetime.datetime.now(datetime.UTC).strftime("%d/%m/%Y  %H:%M:%S ")

# gets the datetime from string formatted as dd-mm-yyyy_HH-MM-SS
def pars_datetime_from_backup_folder_path(path) -> datetime.datetime:
    path = path.rsplit('.', 1)[1]
    [dateStr, timeStr] = path.split('_')
    [dd,mm,yyyy] = dateStr.split('-')
    [HH,MM,SS] = timeStr.split('-')
    dtime = datetime.datetime(year = int(yyyy), month = int(mm), day = int(dd), hour = int(HH), minute = int(MM), second = int(SS), tzinfo=datetime.UTC)
    return dtime

# returns all the backup folders we have for name
def getAllPattern(pattern):
    return [f for f in glob.glob(pattern)]

"""
Seperates the port and the host,
i.e. if full_hostname is <uname>@<ip>:<port> we return (<uname>@<ip>, int(<port>))
if without port we return None for the port i.e. for input <uname>@<ip> we return (<uname>@<ip>, None)
"""
def get_source_name_and_port_from_full_hostname(full_hostname: str) -> Tuple[str, Optional[int]]:
    full_hostname_splitted = full_hostname.split(":")
    if ":" in full_hostname:
        return full_hostname_splitted[0], int(full_hostname_splitted[1])
    else:
        return full_hostname_splitted[0], None

