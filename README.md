# Door Control Program for Islamic Community Cultural Center (IC3)

## Overview

The Door Control Program for the Islamic Community Cultural Center (IC3) is designed to manage the opening and closing of doors based on prayer times and scheduled events. The program runs every morning to determine when the doors need to be unlocked, ensuring smooth and timely access for members of the community.

## Features

- **Automatic Door Control**: Opens and closes doors based on daily prayer times.
- **Event Scheduling**: Accommodates additional events and programs held throughout the week.
- **Customizable Configurations**: Uses configuration files to specify prayer times, exceptions, and logging preferences.
- **Exception Handling**: Allows for exceptions to the regular schedule for special occasions.

## Configuration Files

### `props.json`

This file contains various properties and configurations required by the program:

- `logfile`: Path to the log file.
- `logtofile`: Boolean indicating whether to log to a file.
- `logtostdout`: Boolean indicating whether to log to standard output.
- `salattimefile`: Path to the file containing prayer times (`static.json`).
- `exceptionfile`: Path to the file containing exceptions (`exceptions.txt`).
- `daytable`: Mapping of days of the week to numerical values.
- `imonthtable`: Mapping of Islamic months to numerical values.

### `static.json`

This file contains daily prayer times and associated data:

- `doy`: Day of the year.
- `gmonth`: Gregorian month.
- `gdate`: Gregorian date.
- `gyear`: Gregorian year.
- `iyear`: Islamic year.
- `imonth`: Islamic month.
- `idate`: Islamic date.
- `day`: Day of the week.
- `fajr`, `fajriq`: Fajr prayer times and end times.
- `sunrise`: Sunrise time.
- `dhuhr`, `dhuhriq`: Dhuhr prayer times and end times.
- `asr`, `asriq`: Asr prayer times and end times.
- `maghreb`, `maghrebiq`: Maghreb prayer times and end times.
- `isha`, `ishaiq`: Isha prayer times and end times.

### `exceptions.txt`

This file contains exceptions to the regular schedule. Each line specifies a custom opening and closing time for the doors based on specific dates and times.

#### Format

- `calendar (g/i)`: Specifies if the date is Gregorian (`g`) or Islamic (`i`).
- `[Month]`: The month, represented as an integer (1-12) or `*` for any month.
- `[day_of_month]`: The day of the month, represented as an integer (1-31) or `*` for any day.
- `[day_of_week]`: The day of the week, represented as an integer (0 for Sunday, 6 for Saturday) or `*` for any day.
- `[door_open_time]`: The time when the door should open, in 24-hour format (`HHMM`) or relative to prayer times (e.g., `dhuhriq-30` for 30 minutes before the end of Dhuhr prayer).
- `[door_close_time]`: The time when the door should close, in 24-hour format (`HHMM`) or relative to prayer times (e.g., `dhuhriq+88` for 88 minutes after the end of Dhuhr prayer).

#### Legend

- **Months**:
  - 1: January (Muharram)
  - 2: February (Safar)
  - 3: March (Rabi' al-awwal)
  - 4: April (Rabi' al-thani)
  - 5: May (Jumada al-awwal)
  - 6: June (Jumada al-thani)
  - 7: July (Rajab)
  - 8: August (Sha'ban)
  - 9: September (Ramadan)
  - 10: October (Shawwal)
  - 11: November (Dhu al-Qi'dah)
  - 12: December (Dhu al-Hijjah)

- **Days of the Week**:
  - 0: Sunday
  - 1: Monday
  - 2: Tuesday
  - 3: Wednesday
  - 4: Thursday
  - 5: Friday
  - 6: Saturday

#### Examples

- `g 3 * * 1300 1500`
  - **Gregorian Calendar**
  - Month: March
  - Day of Month: Any day
  - Day of Week: Any day
  - Door Open Time: 1:00 PM
  - Door Close Time: 3:00 PM
  - **Description**: The door opens every day in March from 1:00 PM to 3:00 PM.

- `i 9 * 5 1800 2330`
  - **Islamic Calendar**
  - Month: Ramadan
  - Day of Month: Any day
  - Day of Week: Friday
  - Door Open Time: 6:00 PM
  - Door Close Time: 11:30 PM
  - **Description**: The door opens every Friday in Ramadan from 6:00 PM to 11:30 PM.

- `g * 5 * dhuhriq-30 dhuhriq+88`
  - **Gregorian Calendar**
  - Month: Any month
  - Day of Month: 5th day
  - Day of Week: Any day
  - Door Open Time: 30 minutes before the end of Dhuhr prayer
  - Door Close Time: 88 minutes after the end of Dhuhr prayer
  - **Description**: The door opens on the 5th of every month, 30 minutes before the end of Dhuhr prayer, and closes 88 minutes after the end of Dhuhr prayer.

### Acknowledgements
We would like to thank all members of the Islamic Community Cultural Center (IC3) for their support and contributions to this project.
