import json
from datetime import datetime, timedelta
import subprocess

def logger(s):
    if props['logtofile']:
        with open(props['logfile'], 'a') as f:
            t = datetime.now().strftime('%b %d %Y, %I:%M:%S%p')
            f.write("{ts} | {s}\n".format(ts=t, s=s))
    if props['logtostdout']:
        t = datetime.now().strftime('%b %d %Y, %I:%M:%S%p')
        print("{ts} | {s}".format(ts=t, s=s))

def is_in_month(fmt, mon, values):
    if mon == '*':
        return True  # Matches any month
    if fmt == 'g':
        current_month = values['gmonth']
        numerical_month = props['gmonthtable'][current_month]
    else:
        current_month = values['imonth']
        numerical_month = props['imonthtable'][current_month]
    
    monarr = mon.split(',')

    for m in monarr:
        if not m.isdigit():
            logger("Bad value received for month: [{m}], expected number".format(m=m))
            return False

        if (numerical_month == int(m)):
            return True

    return False

def is_in_date(fmt, date, values):
    if date == '*':
        return True  # Matches any date
    
    if fmt == 'g':
        curdate = int(values['gdate'])
    else:
        curdate =  int(values['idate'])

    datearr = date.split(",")

    for d in datearr:
        if not d.isdigit():
            logger("Bad value received for date: [{d}], expected number".format(d=d))
            return False
    
        if curdate == d:
            return True
        
    return False

def is_in_day(fmt, day, values):
    if day == '*':
        return True  # Matches any day of the week
    
    current_day = values['day']
    current_num_day = props['daytable'][current_day]

    dayarr = day.split(",")

    for d in dayarr:
        if not d.isdigit():
            logger("Bad value received for day: [{d}], expected number".format(d=d))
            return False
    
        if current_num_day == d:
            return True
        
    return False


def adjust_time(prayer_time_str, offset_str):
    prayer_time = datetime.strptime(values[prayer_time_str], "%I:%M %p")
    if offset_str[0] == '+':
        offset_minutes = int(offset_str[1:])
        adjusted_time = prayer_time + timedelta(minutes=offset_minutes)
    elif offset_str[0] == '-':
        offset_minutes = int(offset_str[1:])
        adjusted_time = prayer_time - timedelta(minutes=offset_minutes)
    return adjusted_time.strftime("%H:%M")

def process_exception_time(exception_time):
    if '-' in exception_time or '+' in exception_time:
        if '-' in exception_time:
            parts = exception_time.split('-')
            prayer_time_str = parts[0]
            offset_str = '-' + parts[1]
        elif '+' in exception_time:
            parts = exception_time.split('+')
            prayer_time_str = parts[0]
            offset_str = '+' + parts[1]
        return adjust_time(prayer_time_str, offset_str)
    else:
        return datetime.strptime(exception_time, "%H%M").strftime("%H:%M")

def timetominutes(t):
    h = int(t.split(":")[0])
    m = int(t.split(":")[1])

    return h*60 + m

def applyentry(start, end):
    processed_start = process_exception_time(start)
    processed_end = process_exception_time(end)
    startmin = timetominutes(processed_start)
    endmin = timetominutes(processed_end)

    if endmin <= startmin:
        logger("Lock time [{e}] is before unlock time [{s}]".format(e=endmin, s=startmin))
        #TODO: throw an exception here instead
        return

    #update master array
    minutes[start:end] = [True] * (end - start)

def calculate_prayer_times(prayer_name, unlock_offset, lock_offset):
    prayer_time = values[prayer_name]
    prayer_time = datetime.strptime(prayer_time, "%I:%M %p")

    unlock_time_str = "{pt} - {o}".format(pt=prayer_time.strftime("%H:%M"), o=unlock_offset )
    lock_time_str = "{pt} + {o}".format(pt=prayer_time.strftime("%H:%M"), o=unlock_offset )
        
    applyentry(unlock_time_str, lock_time_str)

def generateat(doorstate, minute):
    t = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0) + timedelta(minutes=minute)
    if doorstate: #open door (unlock)
        command = "echo '/home/pi/scripts/relayon.sh' | at {time}".format(time=t.strftime("%I:%M %p"))
    else: #lock door
        command = "echo '/home/pi/scripts/relayoff.sh' | at {time}".format(time=t.strftime("%I:%M %p"))

    logger(command)
    subprocess.run(command, shell=True, check=True)

##################################################################################################

# Load properties
with open('props.json') as f:
    props = json.load(f)

#master data array
minutes = [False] * 1440

#get today's salat time and date info
now = datetime.now()
reference_date = datetime(2020, 12, 31)
difference = now - reference_date
doy = difference.days

jsonPath = props["salattimefile"]
with open(jsonPath, "r") as times:
    data = json.load(times)

if str(doy) in data:
    values = data[str(doy)]
else:
    logger("data not available")
    exit()

#process exceptions first
with open(props["exceptionfile"], "r") as exceptions:
    for line in exceptions:
        if line[0] == '#' or len(line.strip()) == 0:
            continue

        line = line.strip()
        lineValues = line.split()
        fmt = lineValues[0].strip()
        month = lineValues[1].strip()
        date = lineValues[2].strip()
        day = lineValues[3].strip()
        start = lineValues[4].strip()
        end = lineValues[5].strip()

        if is_in_month(fmt, month, values) and is_in_date(fmt, date, values) and is_in_day(fmt, day, values):
            applyentry(start, end)            




#apply today's iqamah timings
applyentry('fajriq-15', 'fajriq+30')
applyentry('dhuhriq-15', 'dhuhriq+30')
applyentry('asriq-15', 'asriq+30')
applyentry('maghrebiq-15', 'ishaiq+30')

'''
calculate_prayer_times('fajriq', 15, 30)
calculate_prayer_times('dhuhriq', 15, 45)
calculate_prayer_times('asriq', 15, 29)
calculate_prayer_times('maghrebiq', 20, 0)
calculate_prayer_times('ishaiq', 0, 30)
'''

#master data array fully populated at this point
dooropen = minutes[0]

for (i,v) in enumerate(minutes):
    if (v != dooropen): #state changed
        generateat(v, i)
        dooropen = v

