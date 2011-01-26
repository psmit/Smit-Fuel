from google.appengine.ext import db

from datetime import timedelta, date, datetime, time

import itertools
import fuel


class FuelCacheMonth(db.Model):
    year = db.IntegerProperty()
    month = db.IntegerProperty()

    liters = db.FloatProperty(default=0.0)
    km = db.FloatProperty(default=0.0)

    def liters_per_km(self):
        return self.liters/self.km

class FuelCacheWeek(db.Model):
    year = db.IntegerProperty()
    week = db.IntegerProperty()

    liters = db.FloatProperty(default=0.0)
    km = db.FloatProperty(default=0.0)

    def liters_per_km(self):
        return self.liters/self.km


def timedelta_fraction(small,big):
    seconds_small = float(small.days)*3600.0*24.0 + float(small.seconds) + float(small.microseconds)/1000000.0
    seconds_big = float(big.days)*3600.0*24.0 + float(big.seconds) + float(big.microseconds)/1000000.0

    return seconds_small/seconds_big

def updateWeekCache(out):
    for w in FuelCacheWeek.all(): w.delete()


    start_date =  fuel.Refueling.all().order('date').get().date.date()
    first_week_date = start_date - timedelta(start_date.isocalendar()[2]-1)
    last_week_date = date.today() - timedelta(date.today().isocalendar()[2]-1)

    weeks = {}

    cur_week_date = first_week_date


    while cur_week_date <= last_week_date:
        y,w = cur_week_date.isocalendar()[:2]
        weeks[(y,w)] = FuelCacheWeek(year=y,week=w)
        cur_week_date += timedelta(7)

    q = fuel.Refueling.all().order('date')
    cur_refuel = q.get()
    for r in itertools.islice(q,1,None):
        prev_refuel = cur_refuel
        cur_refuel = r

        total_time = cur_refuel.date - prev_refuel.date
        total_liters = prev_refuel.rest_liters + prev_refuel.liters - cur_refuel.rest_liters
        total_km = float(cur_refuel.odo - prev_refuel.odo)

        cur_time = prev_refuel.date

        while 1:

            year, weekno, weekday = cur_time.isocalendar()
            next_week_start = datetime.combine(cur_time.date() + timedelta(8-weekday),time(0,0,0))
            if next_week_start < cur_refuel.date:
                weeks[(year,weekno)].liters += timedelta_fraction(next_week_start-cur_time,total_time) * total_liters
                weeks[(year,weekno)].km += timedelta_fraction(next_week_start-cur_time,total_time) * total_km
                cur_time = next_week_start
            else:
                weeks[(year,weekno)].liters += timedelta_fraction(cur_refuel.date-cur_time,total_time) * total_liters
                weeks[(year,weekno)].km += timedelta_fraction(cur_refuel.date-cur_time,total_time) * total_km
                break

    for w in weeks.itervalues():
        w.save()

    print  >> out, "total km = %.2f" % sum(w.km for w in weeks.itervalues())
    print  >> out,"total l = %.2f" % sum(w.liters for w in weeks.itervalues())


def updateMonthCache(out):
    for m in FuelCacheMonth.all(): m.delete()

    start_date =  fuel.Refueling.all().order('date').get().date.date()
    year,month = start_date.year,start_date.month

    end_year,end_month = date.today().year,date.today().month

    months = {}

    while (year,month) <= (end_year,end_month):
        months[(year,month)] = FuelCacheMonth(year=year,month=month)
        month += 1
        if month == 13:
            year += 1
            month = 1

    q = fuel.Refueling.all().order('date')
    cur_refuel = q.get()
    for r in itertools.islice(q,1,None):
        prev_refuel = cur_refuel
        cur_refuel = r

        total_time = cur_refuel.date - prev_refuel.date
        total_liters = prev_refuel.rest_liters + prev_refuel.liters - cur_refuel.rest_liters
        total_km = float(cur_refuel.odo - prev_refuel.odo)

        cur_time = prev_refuel.date

        while 1:

            year, month = cur_time.year, cur_time.month
            next_month = month + 1
            if next_month == 13:
                next_month = 1
                next_year = year+1
            else:
                next_year = year

            next_month_start = datetime.combine(date(next_year,next_month,1),time(0,0,0))

            if next_month_start < cur_refuel.date:
                months[(year,month)].liters += timedelta_fraction(next_month_start-cur_time,total_time) * total_liters
                months[(year,month)].km += timedelta_fraction(next_month_start-cur_time,total_time) * total_km
                cur_time = next_month_start
            else:
                months[(year,month)].liters += timedelta_fraction(cur_refuel.date-cur_time,total_time) * total_liters
                months[(year,month)].km += timedelta_fraction(cur_refuel.date-cur_time,total_time) * total_km
                break

    for m in months.itervalues():
        m.save()

    print  >> out, "total km = %.2f" % sum(m.km for m in months.itervalues())
    print  >> out,"total l = %.2f" % sum(m.liters for m in months.itervalues())   



        




    
    
    
