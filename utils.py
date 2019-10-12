import datetime 
import glob

def getDatetimePrettyFormat():
    return datetime.datetime.utcnow().strftime("%d/%m/%y  %H:%M:%S ")

# gets the datetime from string formatted as dd-mm-yy_HH-MM-SS
def getDatetimeFromString(formattedDateTime):
    [dateStr, timeStr] = formattedDateTime.split('_')
    [dd,mm,yy] = dateStr.split('-')
    [HH,MM,SS] = timeStr.split('-')
    dtime = datetime.datetime(year = int(yy), month = int(mm), day = int(dd), hour = int(HH), minute = int(MM), second = int(SS))
    return dtime

# returns all the backup folders we have for name
def getAllPattern(pattern):
    return [f for f in glob.glob(pattern)]
