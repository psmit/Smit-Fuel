from datetime import datetime, date
import os
from gviz import gviz_api

from google.appengine.api import users
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext import db

from google.appengine.ext.webapp import template
import fuelcache
import fuelmath

class Refueling(db.Model):
    user = db.UserProperty()
    date = db.DateTimeProperty(auto_now_add=True)
    liters = db.FloatProperty()
    rest_liters = db.FloatProperty(default=0.0)
    liter_price = db.IntegerProperty(default=0)
    total_price = db.IntegerProperty()
    odo = db.IntegerProperty()

    def real_liter_price(self):
        return float(self.liter_price) / 1000.0

    def real_total_price(self):
        return float(self.total_price) / 1000.0

    def __str__(self):
        return "%s %.2f %d" %(self.date, self.liters,self.odo)



class FormPage(webapp.RequestHandler):
    def get(self):
        if users.get_current_user():
            path = os.path.join(os.path.dirname(__file__), 'template/form.html')
            self.response.out.write(template.render(path, { }))
        else:
            self.redirect(users.create_login_url(self.request.uri))


class SubmitPage(webapp.RequestHandler):
    def post(self):
        if users.get_current_user():
            refueling = Refueling()

            refueling.user = users.get_current_user()
            refueling.liters = float(self.request.get('liters'))
            refueling.liter_price = int(round(float(self.request.get('literprice')), 3)* 1000)
            refueling.total_price = int(round((refueling.liter_price * refueling.liters), 0))
            refueling.odo = int(self.request.get('odo'))

            refueling.put()

            fuelmath.update_refueling_list()

            self.redirect('/list')
        else:
            self.redirect(users.create_login_url(self.request.uri))

class ListPage(webapp.RequestHandler):
    def get(self):
        refueling_query = Refueling.all().order('-date')
        refuelings = refueling_query.fetch(100)

        template_values = {
            'refuelings': refuelings,
        }

        path = os.path.join(os.path.dirname(__file__), 'template/list.html')
        self.response.out.write(template.render(path, template_values))


class StatsPage(webapp.RequestHandler):
    def get(self):
        template_values = {
            'refuelings': Refueling.all().order('date'),
            'weekstats' : fuelcache.FuelCacheWeek.all().order('year'),
            'monthstats' : fuelcache.FuelCacheMonth.all().order('year'),
            'url': self.request.environ['HTTP_HOST']
        }

        path = os.path.join(os.path.dirname(__file__), 'template/stats.html')
        self.response.out.write(template.render(path, template_values))


class UpdateStats(webapp.RequestHandler):
    def get(self):
        fuelcache.updateWeekCache(self.response.out)
        fuelcache.updateMonthCache(self.response.out)
        fuelmath.update_refueling_list()


class FuelStats(webapp.RequestHandler):
    def get(self):
        self.response.headers["Content-Type"] = "text/plain"

        dt = gviz_api.DataTable({'date': ('date','Date'),'fuel_price': ('number','Fuel Price'), 'title1': ('string'),'text1': ('string')})

        data_list = []

        for r in  Refueling.all().order('date'):
            if r.liter_price > 0:
                data_list.append({'date':r.date.date(), 'fuel_price': r.real_liter_price(),  'title1':'',  'text1':''})

        dt.LoadData(data_list)
        req_id = 0
        a = self.request.get('tqx')
        for b in a.split(';'):
            if len(b)>2:
                c,d = b.split(':',1)
                if c == 'reqId':
                    req_id = int(d)


        print >> self.response.out, dt.ToJSonResponse(columns_order=("date", "fuel_price", "title1", "text1"),
                                order_by="Date",
                                req_id = req_id)

class WeekStats(webapp.RequestHandler):
    def get(self):
        self.response.headers["Content-Type"] = "text/plain"

        dt = gviz_api.DataTable({'date': ('date','Date'),'usage': ('number','Fuel Usage'), 'title1': ('string'),'text1': ('string'), 'km': ('number', 'Kilometers'), 'title2': ('string'), 'text2': ('string')})

        data_list = []

        for fc in  fuelcache.FuelCacheWeek.all().order('year'):
            if fc.km > 0.0:
                data_list.append({'date':datetime.strptime('%d, %d, 0' % (fc.year,fc.week), '%Y, %U, %w').date(), 'usage': fc.liters_per_km()*100,  'title1':'',  'text1':'',
                                  'km': fc.km, 'title2':'','text2': ''})

        dt.LoadData(data_list)
        req_id = 0
        a = self.request.get('tqx')
        for b in a.split(';'):
            if len(b)>2:
                c,d = b.split(':',1)
                if c == 'reqId':
                    req_id = int(d)

        print >> self.response.out, dt.ToJSonResponse(columns_order=("date", "usage", "title1", "text1","km", "title2", "text2"),
                                order_by="Date",
                                req_id = req_id)


class MonthStats(webapp.RequestHandler):
    def get(self):
        self.response.headers["Content-Type"] = "text/plain"

        dt = gviz_api.DataTable({'date': ('date','Date'),'usage': ('number','Fuel Usage'), 'title1': ('string'),'text1': ('string'), 'km': ('number', 'Kilometers'), 'title2': ('string'), 'text2': ('string')})

        data_list = []

        for fc in  fuelcache.FuelCacheMonth.all().order('year'):
            if fc.km > 0.0:
                data_list.append({'date':date(fc.year,fc.month,1), 'usage': fc.liters_per_km()*100,  'title1':'',  'text1':'',
                                  'km': fc.km, 'title2':'','text2': ''})


        dt.LoadData(data_list)
        req_id = 0
        a = self.request.get('tqx')
        for b in a.split(';'):
            if len(b)>2:
                c,d = b.split(':',1)
                if c == 'reqId':
                    req_id = int(d)

        print >> self.response.out, dt.ToJSonResponse(columns_order=("date", "usage", "title1", "text1","km", "title2", "text2"),
                                order_by="Date",
                                req_id = req_id)


application = webapp.WSGIApplication(
                                     [('/', FormPage),
                                      ('/create', SubmitPage),
                                      ('/list', ListPage),
                                      ('/updatestats', UpdateStats),
                                      ('/stats',StatsPage),
                                      ('/json/fuel', FuelStats),
                                      ('/json/week', WeekStats),
                                      ('/json/month', MonthStats),
                                      ],
                                     debug=True)

def main():
    run_wsgi_app(application)

if __name__ == "__main__":
    main()

