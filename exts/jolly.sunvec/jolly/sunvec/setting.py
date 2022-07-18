import copy
from math import floor

"""
TODO: Improve precision and document/refactor.
TS = Timespan
S = Setting
Valid Infix Operators
TS + TS -> TS (increase span)
TS - TS -> TS (decrease span)
TS * int -> TS (scale span)
S + TS -> S (transpose setting)
S - S -> TS (span between settings)
S << S -> Bool (setting occurs before setting)
"""



class Timespan():
    def __init__(self, years, months, days, hours, minutes, seconds):
        self.years = years
        self.months = months
        self.days = days
        self.hours = hours
        self.minutes = minutes
        self.seconds = seconds
    
    def nonnegative(self):
        return self.to_seconds() >= 0
    
    def from_setting(setting: 'Setting'):
        return Timespan(setting.year, setting.month, setting.day, setting.hour, setting.minute, setting.second)

    def to_seconds(self):
        return 31556952 * self.years + 2628288 * self.months + 86400 * self.days + 3600 * self.hours + 60 * self.minutes + self.seconds

    def from_seconds(total):
        positive = True if total >= 0 else False
        total = total if positive else -total

        year = total // 31556952
        total = total % 31556952

        month = total // 2628288
        total = total % 2628288

        day = total // 86400
        total = total % 86400

        hour = total // 3600
        total = total % 3600

        minute = total // 60
        total = total % 60
  
        second = total

        if not(positive):
            year *= -1; month *= -1; day *= -1; hour *= -1; minute *= -1; second *= -1
        return Timespan(year, month, day, hour ,minute, second)

    def __add__(self, other: 'Timespan'):
        return Timespan(self.years + other.years, \
            self.months + other.months, \
            self.days + other.days, \
            self.hours + other.hours, \
            self.minutes + other.minutes, \
            self.seconds + other.seconds)
    
    def __sub__(self, other: 'Timespan'):
        unconsolidated = Timespan(self.years - other.years, \
            self.months - other.months, \
            self.days - other.days, \
            self.hours - other.hours, \
            self.minutes - other.minutes, \
            self.seconds - other.seconds)
        return(self.__from_seconds(unconsolidated.to_seconds()))

    """
    [__scale(n) is this Timespan scaled by n, REQUIRES:.]
    """
    def __mul__(self, n):
        total = self.to_seconds() * n
        assert self.years >= 0 and self.months >= 0 and self.days >= 0 and self.hours >= 0 and self.minutes >= 0

        years = total // 31556952
        total = total % 31556952

        months = total // 2628288
        total = total % 2628288

        days = total // 86400
        total = total % 86400

        hours = total // 3600
        total = total % 3600

        minutes = total // 60
        total = total % 60
  
        seconds = total
        return Timespan(years, months, days, hours, minutes, seconds)



"""
Setting is an immutable representation of a date.
"""
class Setting():
    
    def is_not_leap(year): 
        return year%4 != 0

    def max_of_month(self, month, year):
        maxes = [29,31,28,31,30,31,30,31,31,30,31,30,31]
        return maxes[month * ( 1 - (year%4 == 0)*(month == 2))]

    """
    [valid_day(day, month, year) is True if [day] is a valid day of the [month] in the [year].]
    """
    def valid_day(self, day, month, year):
        return True if 1 <= month and month <= 12 and day >= 1 and day <= self.max_of_month(month, year) else False
            
    """
    [__init__(lat, long, year, month, day, hour, minute, second, timezone)] is a time and place on Earth.
    NOTE: Year must be of range 1901 to 2099; time change is not accounted for.
    """
    def __init__(self, lat, long, year, month, day, hour, minute, second, timezone):
        self.lat = lat if -90 <= lat and lat <= 90 else (print(F"JOLLY.SUNVEC..invalid latitude={lat}, range -90 to 90, default 0"),0)[1]  # Functional python hack? Lol.. Why does it even evaluate that print?
        self.long = long if -180 <= long and long <= 180 else (print(F"JOLLY.SUNVEC..invalid longitude={long}, range -180 to 180, default 0"), 0)[1]
        self.year = year if 1901 <= year and year <= 2099 else (print(F"JOLLY.SUNVEC..invalid year={year}, range 1901 to 2099, default 2022"), 2022)[1]
        self.month = month if 1 <= month and month <= 12 else (print(F"JOLLY.SUNVEC..invalid month={month}, default 7"), 7)[1]
        self.day = day if self.valid_day(day, self.month, self.year) else (print(F"JOLLY.SUNVEC..invalid {day}, default 12"), 12)[1]
        self.hour = hour if 0 <= hour and hour <= 23 else (print(F"JOLLY.SUNVEC..invalid hour={hour}, default 12"), 12)[1]
        self.minute = minute if 0 <= minute and minute <= 59 else (print(F"JOLLY.SUNVEC..invalid minute={minute}, default 0"), 0)[1]
        self.second = second if 0 <= second and second <= 59 else (print(F"JOLLY.SUNVEC..invalid second={second}, default 0"), 0)[1]
        self.timezone = timezone if -14 <= timezone and timezone <= 12 else (print(F"JOLLY.SUNVEC..invalid timezone={timezone}, default -6"), -6)[1]  #  TODO: Automate timezone from coordinates? Possible.
        self.date = (self.year, self. month, self.day, self.hour, self.minute, self.second, self.timezone)
        self.loc = (self.lat, self.long)

    """
    [setting + timespan] is the [setting] advanced for the interval of time in [timespan].
    """
    def __eq__(self, setting2 : 'Setting'):
        return self.date == setting2.date and self.loc == setting2.loc

    def get_date(self):
        return copy.deepcopy(self.date)

    def get_loc(self):
        return copy.deepcopy(self.loc)

    def __add__(self, interval: Timespan):
        new_seconds = self.second + interval.seconds
        new_minutes = self.minute + interval.minutes
        new_hours = self.hour + interval.hours
        new_day = self.day  #We manually step through larger units later to make sure month transitions are handled.
        new_month = self.month
        new_year = self.year

        # Calculate how many days to advance; set smaller units.
        new_minutes += (new_seconds // 60); new_seconds = new_seconds % 60
        new_hours += (new_minutes // 60); new_minutes = new_minutes % 60
        days_to_step = interval.days + (new_hours // 24); new_hours = new_hours % 24

        for _ in range(0, int(days_to_step)):
            if not(self.valid_day(new_day, self.month, self.year)):
                new_day = 1
                new_month += 1

            if new_month > 12:
                new_month = 1
                new_year += 1

            new_day += 1
        
        # The -1 +1 stuff is because Settings have months stored [1...12] where Timespans go [0...11]. 
        new_year += (new_month - 1 + interval.months) // 12
        new_month = ((new_month + (interval.months % 12) - 1)) % 12 + 1  

        
        return(Setting(self.lat, self.long, int(new_year), int(new_month), int(new_day), \
             int(new_hours), int(new_minutes), int(new_seconds), int(self.timezone)))
    
    def __sub__(self, setting: 'Setting'):
        return Timespan.from_seconds(Timespan.to_seconds(Timespan.from_setting(self)) - \
             Timespan.to_seconds(Timespan.from_setting(setting)))

    """
    [setting1 << setting2] is True if the date of setting1 occurs no later than the date of setting2.
    NOTE: Timezones and locations must match.
    """
    def __lshift__(self, setting2 : 'Setting'):
        return Timespan.from_setting(self).to_seconds() < Timespan.from_setting(setting2).to_seconds()


    def __str__(self):
        name_month = ["January","February","March","April","May","June","July","August","September","October","November","December"]
        name_day = ["th","st","nd","rd","th","th","th","th","th","th"]
        time = ["12","1","2","3","4","5","6","7","8","9","10","11","12","1","2","3","4","5","6","7","8","9","10","11"]
        time_suffix = ["AM","PM"]
        min_str = str(self.minute) if 0 <= self.minute and self.minute >= 10 else "0"+str(self.minute) 
        sec_str = str(self.second) if 0 <= self.second and self.second >= 10 else "0"+str(self.second) 
        if 0 <= self.lat:
            coordNS = F"{str(round(self.lat,3))} N"
        else:
            coordNS = F"{str(round(180-self.lat,3))} S" 
        if 0 <= self.long:
            coordEW = F"{str(round(self.long,3))} E"
        else:
            coordEW = F"{str(round(-self.long,3))} W" 
        coord = F"({coordNS}, {coordEW})"
        utc = F"UTC {self.timezone}:00"

        return(F"{name_month[self.month-1]} {self.day}{name_day[self.day%10]}, {self.year} \
         \n{time[self.hour]}:{min_str}:{sec_str}{time_suffix[self.hour//12]} \n@ {coord} {utc}")


class SettingRange():
    ctr = 0
    """
    [SettingRange(setting_start, setting_end)] is the time period between the two settings.
    """
    def __init__(self, setting_start:Setting, setting_end:Setting):
        if setting_start << setting_end:
            self.start = setting_start
            self.end = setting_end

            self.span = self.end - self.start 
        else:
            print("JOLLY.SUNVEC..start date !<< end date or locations mismatch, defaulting to start date -> start date")
            self.start = setting_start
            self.end = setting_start

            self.span = self.end - self.start 

    def change_start(self, replacement_setting:Setting):
        if replacement_setting << self.end:
            self.start = replacement_setting

            self.span = self.end - self.start
        else:
            print("JOLLY.SUNVEC..start cannot occur later than the end")
    
    def change_end(self, replacement_setting:Setting):
        if self.start << replacement_setting:
            self.end = replacement_setting

            self.span = self.end - self.start
        else:
            print("JOLLY.SUNVEC..end cannot occur before the start")

    def get_start_date(self):
        return copy.deepcopy(self.start.date)

    def get_end_date(self):
        return copy.deepcopy(self.end.date)

    def get_loc(self):
        return copy.deepcopy(self.start.loc)
    
    def subdiv_range(self, divs):
        settings = []
        for i in range(0, divs):
            settings.append(self.start + (self.span * (i/divs)))
        settings.append(self.end)
        return settings

    def increment_range(self, inc: Timespan, num):
        assert inc.to_seconds() > 0
        settings = []
        i = 0
        while i < num:
            self.start += inc
            settings.append(self.start)
            i += 1
        return settings

    def increment_until_range(self, inc: Timespan):
        if (inc.to_seconds() <= 0):
            print("JOLLY.SUNVEC..non-positive increments are not permitted, defaulting to 1 second")
            inc = Timespan(0,0,0,0,0,1)
        elif (self.end - self.start).to_seconds() / inc.to_seconds() > 100:
            print("JOLLY.SUNVEC..increment too small to bridge starting and ending date, limiting to 100 steps")
        settings = []
        i = 0
        while (self.end - (self.start + inc)).nonnegative():
            self.start += inc
            settings.append(self.start + inc)
            i += 1
            if i == 101:  
                break
        return settings
    
