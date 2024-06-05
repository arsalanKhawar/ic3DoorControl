from datetime import datetime, timedelta
import json
import subprocess

# Load properties
with open('props.json') as f:
    props = json.load(f)

def logger(s):
    if props['logtofile']:
        with open(props['logfile'], 'a') as f:
            t = datetime.now().strftime('%b %d %Y, %I:%M:%S%p')
            f.write("{ts} | {s}\n".format(ts = t, s = s))
    if props['logtostdout']:
        t = datetime.now().strftime('%b %d %Y, %I:%M:%S%p')
        print("{ts} | {s}".format(ts = t, s = s))

# Returns true if today falls within the month parameter range
def is_in_month(fmt, mon, values):
    if mon == '*':
        return True  # Matches any month

    if fmt == 'g':
        current_month = values['gmonth']
    else:
        current_month = values['imonth']
    
    try:
        # Check if mon is a string name and convert it to an integer
        if not mon.isdigit():
            if fmt == 'g':
                mon = datetime.strptime(mon, '%B').month
            else:
                mon = props['imonthtable'][mon]
        mon = int(mon)

        # Convert current_month to an integer if it is a name
        if not current_month.isdigit():
            if fmt == 'g':
                current_month = datetime.strptime(current_month, '%B').month
            else:
                current_month = props['imonthtable'][current_month]
        current_month = int(current_month)
        return current_month == int(mon)
    except KeyError:
        return False

# Returns true if today falls within the date parameter range
def is_in_date(fmt, date, values):
    if date == '*':
        return True  # Matches any date
    return int(values['day']) == int(date)

# Returns true if today falls within the day parameter range
def is_in_day(fmt, day, values):
    if day == '*':
        return True  # Matches any day of the week
    current_day = datetime.now().weekday()
    # Adjust the current_day to match the day table in props
    current_day = (current_day + 1) % 7  # Adjust to match Sunday=0, Monday=1, etc.
    return current_day == int(day)

def adjust_time(prayer_time_str, offset_str):
    prayer_time = datetime.strptime(values[prayer_time_str], "%I:%M %p")
    if offset_str[0] == '+':
        offset_minutes = int(offset_str[1:])
        adjusted_time = prayer_time + timedelta(minutes=offset_minutes)
    elif offset_str[0] == '-':
        offset_minutes = int(offset_str[1:])
        adjusted_time = prayer_time - timedelta(minutes=offset_minutes)
    return adjusted_time.strftime("%H%M")

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
        return datetime.strptime(exception_time, "%H%M").strftime("%H%M")

def is_within_any_range(time_to_check, ranges):
    # First convert the check time to 24-hour format
    time_to_check = datetime.strptime(time_to_check, "%I:%M %p").strftime("%H%M")
    time_to_check = datetime.strptime(time_to_check, "%H%M")
    
    for time_range in ranges:
        start_time = datetime.strptime(time_range[0], "%H%M")
        end_time = datetime.strptime(time_range[1], "%H%M")
        if start_time <= time_to_check <= end_time:
            return True
    return False

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

todaysExceptions = []
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
            processed_start = process_exception_time(start)
            processed_end = process_exception_time(end)
            todaysExceptions.append([processed_start, processed_end])

print("Initial Exceptions:", todaysExceptions)

unlockTimes = []
lockTimes = []

def calculate_prayer_times(prayer_name, unlock_offset, lock_offset):
    prayer_time = values[prayer_name]
    prayer_time = datetime.strptime(prayer_time, "%I:%M %p")

    if unlock_offset != 0:
        unlock_time = prayer_time - timedelta(minutes=unlock_offset)
        unlock_time_str = unlock_time.strftime("%I:%M %p")
        if not is_within_any_range(unlock_time_str, todaysExceptions):
            unlockTimes.append(unlock_time_str)

    if lock_offset != 0:
        lock_time = prayer_time + timedelta(minutes=lock_offset)
        lock_time_str = lock_time.strftime("%I:%M %p")
        if not is_within_any_range(lock_time_str, todaysExceptions):
            lockTimes.append(lock_time_str)

calculate_prayer_times('fajriq', 15, 30)
calculate_prayer_times('dhuhriq', 15, 45)
calculate_prayer_times('asriq', 15, 29)
calculate_prayer_times('maghrebiq', 20, 0)
calculate_prayer_times('ishaiq', 0, 30)

# Add exceptions directly to the unlock and lock times to ensure they cover the entire period
for time_range in todaysExceptions:
    unlockTimes.append(time_range[0])
    lockTimes.append(time_range[1])

print("Unlock Times:", unlockTimes)
print("Lock Times:", lockTimes)

'''
for time in unlockTimes:
    command = "echo '/home/pi/scripts/relayon.sh' | at " + str(time)
    subprocess.run(command, shell=True, check=True)

for time in lockTimes:
    command = "echo '/home/pi/scripts/relayon.sh' | at " + str(time)
    subprocess.run(command, shell=True, check=True)
'''

print(doy)
