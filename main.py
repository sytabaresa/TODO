from google.appengine.ext import db
from google.appengine.api import users
import webapp2 as webapp
import jinja2
import os
import logging
import datetime

jinja_environment = jinja2.Environment(
	loader=jinja2.FileSystemLoader(os.path.dirname(__file__)))

class Task(db.Model):
	"""Something to do"""
	text = db.StringProperty()
	date = db.DateTimeProperty(auto_now_add=True)

class MainPage(webapp.RequestHandler):
	def get(self):
		tasks = db.GqlQuery("SELECT * "
		            "FROM Task "
		            "ORDER BY date DESC")

		template_values = {
		   'age': 25,
		   'tasks': tasks,
		}

		template = jinja_environment.get_template('templates/index.html')
		self.response.out.write(template.render(template_values))

class Inserter(webapp.RequestHandler):
	def post(self):
		task = Task()
		task.text = self.request.get('tasktext')
		task.put()
		self.redirect('/')

class Deleter(webapp.RequestHandler):
	def post(self):
		taskid = int(self.request.get('taskid'))
		task = Task.get_by_id(taskid)
#		logging.info("Delete: Taskid=%s"%taskid)
#		logging.info("Delete: task=%s"%task)
		task.delete()
		self.redirect('/')

app = webapp.WSGIApplication([
	('/', MainPage),
	('/insertTask', Inserter),
	('/deleteTask', Deleter),
	],
	debug=True)

