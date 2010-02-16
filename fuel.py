import cgi
import os

from google.appengine.api import users
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext import db

from google.appengine.ext.webapp import template

class Refueling(db.Model):
	author = db.UserProperty()
	date = db.DateTimeProperty(auto_now_add=True)
	liters = db.FloatProperty()
	liter_price = db.IntegerProperty()
	total_price = db.IntegerProperty()
	odo = db.IntegerProperty
	full_tank = db.BooleanProperty()

class FormPage(webapp.RequestHandler):
	def get(self):
		path = os.path.join(os.path.dirname(__file__), 'form.html')
		self.response.out.write(template.render(path))

class SubmitPage(webapp.RequestHandler):
	def post(self):
		
		
class ConfirmPage(webapp.RequestHandler):
	def get(self):
		
	
application = webapp.WSGIApplication(
                                     [('/', FormPage),
                                      ('/create', SubmitPage)],
                                     debug=True)

def main():
	run_wsgi_app(application)

if __name__ == "__main__":
	main()

