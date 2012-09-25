from google.appengine.ext import db
from google.appengine.api import users
import webapp2 as webapp
import jinja2
import os
import logging
import datetime

jinja_environment = jinja2.Environment(
	loader=jinja2.FileSystemLoader(os.path.dirname(__file__)))

def myFormatDate(date):
	return date.strftime('%d.%m.%Y')

class Task(db.Model):
	"""Something to do"""
	text = db.StringProperty()
	date = db.DateTimeProperty(auto_now_add=True)
	datedone = db.DateProperty()
	done = db.BooleanProperty(default=False)

	def formattedDateDone(self):
		return myFormatDate(self.datedone)

class Receipt(db.Model):
	"""Record of something I bought"""
	money = db.FloatProperty()
	date = db.DateTimeProperty(auto_now_add=True)
	description = db.StringProperty()
	method = db.CategoryProperty()

	def formattedDate(self):
		return myFormatDate(self.date)

class MainPage(webapp.RequestHandler):
	def get(self):
		tasks = db.GqlQuery("SELECT * "
		            "FROM Task "
		            "WHERE done = FALSE "
		            "ORDER BY date DESC")
		done = db.GqlQuery("SELECT * "
		                   "FROM Task "
		                   "WHERE done = TRUE "
		                   "ORDER BY date DESC LIMIT 4")
		receipts = db.GqlQuery("SELECT * "
		                       "FROM Receipt "
		                       "ORDER BY date DESC")

		template_values = {
		   'tasks': tasks,
		   'done': done,
		   'receipts': receipts,
		}

		template = jinja_environment.get_template('templates/index.html')
		self.response.out.write(template.render(template_values))

class TaskInserter(webapp.RequestHandler):
	def post(self):
		task = Task()
		task.text = self.request.get('tasktext')
		task.put()
		self.redirect('/')

class DoneHandler(webapp.RequestHandler):
	def post(self):
		taskid = int(self.request.get('taskid'))
		task = Task.get_by_id(taskid)
		task.done = True
		task.datedone = datetime.date.today()
		logging.info(task.getDateDone())
		task.put()
		self.redirect('/')

class ReceiptInserter(webapp.RequestHandler):
	def post(self):
		receipt = Receipt()
		receipt.money = float(self.request.get('receiptmoney'))
		receipt.description = self.request.get('receiptdescription')
		receipt.method = self.request.get('receiptmethod')
		receipt.put()
		self.redirect('/')

app = webapp.WSGIApplication([
	('/', MainPage),
	('/insertTask', TaskInserter),
	('/doneTask', DoneHandler),
	('/insertReceipt', ReceiptInserter),
	],
	debug=True)

