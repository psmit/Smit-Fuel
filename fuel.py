import cgi
import os

from google.appengine.api import users
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext import db

from google.appengine.ext.webapp import template

class Refueling(db.Model):
	user = db.UserProperty()
	date = db.DateTimeProperty(auto_now_add=True)
	liters = db.FloatProperty()
	liter_price = db.IntegerProperty()
	total_price = db.IntegerProperty()
	odo = db.IntegerProperty
	full_tank = db.BooleanProperty()

class FormPage(webapp.RequestHandler):
	def get(self):
		if users.get_current_user():
			path = os.path.join(os.path.dirname(__file__), 'form.html')
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
			refueling.total_price = int(round((refueling.liter_price * refueling.liters) / 10, 0))
			refueling.odo = int(self.request.get('odo'))
			
			refueling.put()
			self.redirect('/list')
		else:
			self.redirect(users.create_login_url(self.request.uri))
		
class ListPage(webapp.RequestHandler):
	def get(self):
		refueling_query = Refueling.all().order('-date')
		refuelings = refueling_query.fetch(10)
		
		template_values = {
			'refuelings': refuelings,
		}
		
		path = os.path.join(os.path.dirname(__file__), 'list.html')
		self.response.out.write(template.render(path, template_values))
	
application = webapp.WSGIApplication(
                                     [('/', FormPage),
                                      ('/create', SubmitPage),
                                      ('/list', ListPage)],
                                     debug=True)

def main():
	run_wsgi_app(application)

if __name__ == "__main__":
	main()

