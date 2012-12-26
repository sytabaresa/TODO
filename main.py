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

class Bill(db.Model):
	"""Record of something I bought"""
	money = db.FloatProperty()
	date = db.DateTimeProperty(auto_now_add=True)
	description = db.StringProperty()
	method = db.CategoryProperty()

	def formattedDate(self):
		return myFormatDate(self.date)

class Wish(db.Model):
	"""Something I should buy"""
	description = db.StringProperty()
	reference = db.StringProperty()

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
		bills = db.GqlQuery("SELECT * "
		                       "FROM Bill "
		                       "ORDER BY date DESC")
		wishes = db.GqlQuery("SELECT * "
		                     "FROM Wish")

		activetab = self.request.get('activetab')
		if not activetab:
			activetab = 'bills'
		#logging.info('activetab %s'%activetab)

		template_values = {
		'tasks': tasks,
		'done': done,
		'bills': bills,
		'wishes': wishes,
		'activetab': activetab,
		}

		template = jinja_environment.get_template('templates/index.html')
		self.response.out.write(template.render(template_values))

class TaskInserter(webapp.RequestHandler):
	def post(self):
		task = Task()
		task.text = self.request.get('tasktext')
		task.put()
		self.redirect('/')

class Eversticky(webapp.RequestHandler):
	def get(self):
		self.response.headers['Content-Type'] = 'text/plain'
		tasks = db.GqlQuery("SELECT * "
		         "FROM Task "
		         "WHERE done = FALSE "
		         "ORDER BY date DESC")
		logging.info('tasks %s'%tasks)
		lines = []
		for task in tasks:
			lines.append(task.text)
		self.response.out.write('\n'.join(lines))

class DoneHandler(webapp.RequestHandler):
	def post(self):
		taskid = int(self.request.get('taskid'))
		task = Task.get_by_id(taskid)
		task.done = True
		task.datedone = datetime.date.today()
		task.put()
		self.redirect('/')

class BillInserter(webapp.RequestHandler):
	def post(self):
		bill = Bill()
		bill.money = float(self.request.get('bill-money'))
		bill.description = self.request.get('bill-description')
		bill.method = self.request.get('bill-method')
		bill.put()
		self.redirect('/?activetab=bills')

class BillDeleter(webapp.RequestHandler):
	def post(self):
		billid = int(self.request.get('billid'))
		bill = Bill.get_by_id(billid)
		bill.delete()
		self.redirect('/?activetab=bills')

class WishInserter(webapp.RequestHandler):
	def post(self):
		wish = Wish()
		wish.description = self.request.get('wishdescription')
		wishref = self.request.get('wishreference')
		if wishref:
			wish.reference = wishref
		wish.put()
		self.redirect('/?activetab=tobuy')

class WishDeleter(webapp.RequestHandler):
	def post(self):
		wishid = int(self.request.get('wishid'))
		wish = Wish.get_by_id(wishid)
		wish.delete()
		self.redirect('/?activetab=tobuy')

app = webapp.WSGIApplication([
	('/', MainPage),
	('/insertTask', TaskInserter),
	('/doneTask', DoneHandler),
	('/insertBill', BillInserter),
	('/deleteBill', BillDeleter),
	('/insertWish', WishInserter),
	('/deleteWish', WishDeleter),
	('/eversticky', Eversticky),
	],
	debug=True)

