from datetime import datetime, timedelta
import json
import subprocess

def adjust_time(prayer_time_str, offset_str):
    prayer_time = datetime.strptime(values[prayer_time_str], "%I:%M %p")
    if offset_str[0] == '+':
        offset_minutes = int(offset_str[1:])
        adjusted_time = prayer_time + timedelta(minutes=offset_minutes)
    elif offset_str[0] == '-':
        offset_minutes = int(offset_str[1:])
        adjusted_time = prayer_time - timedelta(minutes=offset_minutes)
    return adjusted_time.strftime("%I:%M %p")

def get_time_in_range(time_to_check, ranges, get_end_time=False):
    time_to_check = datetime.strptime(time_to_check, "%I:%M %p")
    for time_range in ranges:
        try:
            start_time = datetime.strptime(time_range[0], "%I:%M %p")
            end_time = datetime.strptime(time_range[1], "%I:%M %p")
            if start_time <= time_to_check <= end_time:
                return end_time.strftime("%I:%M %p") if get_end_time else start_time.strftime("%I:%M %p")
        except ValueError:
            continue
    return None

def is_within_any_range(time_to_check, ranges):
    time_to_check = datetime.strptime(time_to_check, "%I:%M %p")
    for time_range in ranges:
        start_time = datetime.strptime(time_range[0], "%I:%M %p")
        end_time = datetime.strptime(time_range[1], "%I:%M %p")
        if start_time <= time_to_check <= end_time:
            return True
    return False

now = datetime.now()
reference_date = datetime(2020, 12, 31)
difference = now - reference_date
doy = difference.days

jsonPath = "static.json"
with open(jsonPath, "r") as times:
    data = json.load(times)

if str(doy) in data:
    values = data[str(doy)]
else:
    print("data not available")
    exit()

todaysExceptions = []
with open("exceptions.txt", "r") as exceptions:
    for line in exceptions:
        line = line.strip()
        lineValues = line.split()
        month = lineValues[0]
        day = lineValues[1]
        
        if (values['gmonth'].lower() == month.lower() or values['imonth'].lower() == month.lower()) and values['day'] == day:
            todaysExceptions.append([lineValues[2], lineValues[3]])
        elif values['day'] == day and month == '0':
            todaysExceptions.append([lineValues[2], lineValues[3]])
        elif (values['gmonth'].lower() == month.lower() or values['imonth'].lower() == month.lower()) and day == '0':
            todaysExceptions.append([lineValues[2], lineValues[3]])

print("Initial Exceptions:", todaysExceptions)

# Change exceptions into time strings
for i in range(len(todaysExceptions)):
    for j in range(len(todaysExceptions[i])):
        if '-' in todaysExceptions[i][j] or '+' in todaysExceptions[i][j]:
            if '-' in todaysExceptions[i][j]:
                parts = todaysExceptions[i][j].split('-')
                prayerTimeString = parts[0]
                offsetString = '-' + parts[1]
            elif '+' in todaysExceptions[i][j]:
                parts = todaysExceptions[i][j].split('+')
                prayerTimeString = parts[0]
                offsetString = '+' + parts[1]
            todaysExceptions[i][j] = adjust_time(prayerTimeString, offsetString)
        else:
            if 'AM' in todaysExceptions[i][j]:
                todaysExceptions[i][j] = todaysExceptions[i][j].replace('AM', ' AM')
            elif 'PM' in todaysExceptions[i][j]:
                todaysExceptions[i][j] = todaysExceptions[i][j].replace('PM', ' PM')

print("Processed Exceptions:", todaysExceptions)

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
        







