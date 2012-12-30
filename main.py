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

class BillCategory(db.Model):
	"""A category of expenses"""
	title = db.StringProperty()
	display_order = db.IntegerProperty()
	display_section = db.IntegerProperty()

	@staticmethod
	def loadCategoriesFromFile():
		f = file("./categories.csv")
		for line in f.readlines():
			cols = line.split(',')
			newCat = BillCategory()
			newCat.display_order = int(cols[0])
			newCat.display_section = int(cols[1])
			newCat.title = cols[2].strip('\n')
			newCat.put()

class Bill(db.Model):
	"""Record of something I bought"""
	money = db.FloatProperty()
	cents = db.StringProperty()
	date = db.DateTimeProperty(auto_now_add=True)
	category = db.ReferenceProperty(BillCategory)
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
		this_year = datetime.datetime.now().year
		this_month = datetime.datetime.now().month
		bills = db.GqlQuery("SELECT * "
	                       "FROM Bill "
	                       "WHERE date >= DATETIME('"+str(this_year)+"-"+str(this_month)+"-01 00:00:00') "
	                       "ORDER BY date DESC")
		wishes = db.GqlQuery("SELECT * "
		                     "FROM Wish")
		categories = db.GqlQuery("SELECT * "
		                         "FROM BillCategory "
		                         "ORDER BY display_order")

		this_month_expenses = 0
		for bill in bills:
			if bill.money < 0 and bill.date.month == datetime.datetime.now().month:
				this_month_expenses += abs(bill.money)

		activetab = self.request.get('activetab')
		if not activetab:
			activetab = 'bills'
		#logging.info('activetab %s'%activetab)

		template_values = {
			'tasks': tasks,
			'done': done,
			'bills': bills,
			'categories': categories,
			'wishes': wishes,
			'this_month_expenses': this_month_expenses,
			'activetab': activetab,
		}

		# In case you want to load categories data to local database
		#BillCategory.loadCategoriesFromFile()

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

		moneystr = self.request.get('bill-money')
		moneystr = moneystr.replace(',','.')
		bill.money = float(moneystr)
		#bill.cents = str(int(abs(round(asd*100))%100)) # Not necessary anymore, just for info
		bill.category = BillCategory.get(self.request.get('bill-category'))
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

