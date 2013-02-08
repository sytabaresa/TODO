import json as simplejson
from google.appengine.ext import db
from google.appengine.api import users
import webapp2 as webapp
import jinja2
import os
import logging
import datetime

jinja_environment = jinja2.Environment(
	loader=jinja2.FileSystemLoader(os.path.dirname(__file__)))

from oauth2client.appengine import OAuth2Decorator
from apiclient.discovery import build

use_google_auth = True
allowed_users = ['andre.staltz@gmail.com', 'mesituominen@gmail.com', 'mesi.tuominen@gmail.com',
                 'mesimedeiros@gmail.com']
atividades_cal = '862ukq5llt4v0i9t6bl8shv8e0@group.calendar.google.com'
oauth_decorator = OAuth2Decorator(
	client_id='235295882530.apps.googleusercontent.com',
	client_secret='W6ok7IKTiWg-xy_E4ZTUkIZn',
	scope='https://www.googleapis.com/auth/calendar'
)
gcal_service = build('calendar', 'v3')
gcal_timeformat = "%Y-%m-%dT%H:%M:%S"


def myFormatDate(date):
	return date.strftime('%d.%m.%Y')


def userForbidden():
	http = None
	user = None
	if use_google_auth:
		http = oauth_decorator.http()
		user = users.get_current_user()
		if user.email() not in allowed_users:
			return True
	return False


class Task(db.Model):
	"""Something to do"""
	text = db.StringProperty()
	date = db.DateTimeProperty(auto_now_add=True)
	dateplay = db.DateTimeProperty()
	datedone = db.DateTimeProperty()
	playing = db.BooleanProperty(default=False)
	done = db.BooleanProperty(default=False)
	eventId = db.StringProperty()

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

	@staticmethod
	def loadSampleBillsFromFile():
		f = file('./bills.csv')
		for line in f.readlines():
			cols = line.split(',')
			newBill = Bill()
			newBill.money = float(cols[0])
			newBill.method = cols[1]
			query = "SELECT * FROM BillCategory WHERE title = '%s'" % cols[2].strip()
			category = db.GqlQuery(query)[0]
			newBill.category = category
			newBill.put()


class Wish(db.Model):
	"""Something I should buy"""
	description = db.StringProperty()
	reference = db.StringProperty()


class MainPage(webapp.RequestHandler):
	@oauth_decorator.oauth_required
	def get(self):
		http = None
		user = None
		if use_google_auth:
			# Get the authorized Http object created by the decorator
			http = oauth_decorator.http()
			user = users.get_current_user()
			if user.email() not in allowed_users:
				self.response.status = 403
				self.response.out.write("Sorry, you are not allowed")
				return

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
		                    "WHERE date >= DATETIME('" + str(this_year) + "-" + str(this_month) + "-01 00:00:00') "
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

		user_link = None
		if use_google_auth:
			user_link = users.create_logout_url('/') if user else users.create_login_url('/')

		template_values = {
		'tasks': tasks,
		'done': done,
		'bills': bills,
		'categories': categories,
		'wishes': wishes,
		'this_month_expenses': this_month_expenses,
		'activetab': activetab,
		'user': user,
		'user_link': user_link,
		}

		# In case you want to load categories data to local database
		#BillCategory.loadCategoriesFromFile()

		template = jinja_environment.get_template('templates/index.html')
		self.response.out.write(template.render(template_values))


class ViewStatistics(webapp.RequestHandler):
	@oauth_decorator.oauth_required
	def get(self):
		http = None
		user = None
		if use_google_auth:
		# Get the authorized Http object created by the decorator
			http = oauth_decorator.http()
			user  = users.get_current_user()
			if user.email() not in allowed_users:
				self.response.status = 403
				self.response.out.write("Sorry, you are not allowed")
				return
		template = jinja_environment.get_template('templates/statistics.html')
		self.response.out.write(template.render({}))


class Statistics(webapp.RequestHandler):
	@oauth_decorator.oauth_required
	def post(self):
		http = None
		user = None
		if use_google_auth:
		# Get the authorized Http object created by the decorator
			http = oauth_decorator.http()
			user  = users.get_current_user()
			if user.email() not in allowed_users:
				self.response.status = 403
				self.response.out.write("Sorry, you are not allowed")
				return

			# In case you want to load data to local database
			#		BillCategory.loadCategoriesFromFile()
			#		Bill.loadSampleBillsFromFile()

		this_year = datetime.datetime.now().year
		this_month = datetime.datetime.now().month
		categories = db.GqlQuery("SELECT * FROM BillCategory")
		bills = db.GqlQuery("SELECT * "
		                    "FROM Bill "
		                    "WHERE date >= DATETIME('" + str(this_year) + "-" + str(this_month) + "-01 00:00:00') "
		                                                                                          "ORDER BY date DESC")
		categories_expenses = {}
		for cat in categories:
			categories_expenses[cat.title] = []
		for bill in bills:
			categories_expenses[bill.category.title].append(bill)
		for cat in categories:
			if isinstance(categories_expenses[cat.title], list):
				sum = 0
				for bill in categories_expenses[cat.title]:
					if bill.money < 0:
						sum += abs(bill.money)
				categories_expenses[cat.title] = sum

		expenses = sorted(categories_expenses, key=categories_expenses.get)
		for i in xrange(len(expenses)):
			expenses[i] = [expenses[i], float(int(categories_expenses[expenses[i]] * 100)) / 100.0]
		expenses.reverse()

		while expenses[-1][1] == 0:
			expenses.pop()

		data = simplejson.dumps(expenses)
		self.response.headers['Content-Type'] = 'application/json'
		self.response.out.write(data)


class TaskInserter(webapp.RequestHandler):
	def post(self):
		task = Task()
		task.text = self.request.get('tasktext')
		task.put()
		self.redirect('/?activetab=todo')


class EET(datetime.tzinfo):
	def utcoffset(self, dt):
		return datetime.timedelta(hours=2)

	def dst(self, dt):
		return datetime.timedelta(0)


class TaskPlay(webapp.RequestHandler):
	@oauth_decorator.oauth_aware
	def post(self):
		http = None
		if use_google_auth:
			http = oauth_decorator.http()

		taskid = int(self.request.get('taskid'))
		task = Task.get_by_id(taskid)

		now = datetime.datetime.now(EET())
		later = now + datetime.timedelta(0, 900)

		event = {
		'kind': 'calendar#event',
		'summary': task.text,
		'start': {
		'dateTime': now.strftime(gcal_timeformat),
		'timeZone': 'Europe/Helsinki'
		},
		'end': {
		'dateTime': later.strftime(gcal_timeformat),
		'timeZone': 'Europe/Helsinki'
		},
		}

		if use_google_auth:
			created_event = gcal_service.events().insert(calendarId=atividades_cal, body=event).execute(http=http)
			task.eventId = created_event['id']

		task.playing = True
		task.dateplay = datetime.datetime.now(EET())
		task.put()
		self.redirect('/?activetab=todo')


class TaskStop(webapp.RequestHandler):
	@oauth_decorator.oauth_aware
	def post(self):
		http = None
		if use_google_auth:
			http = oauth_decorator.http()

		taskid = int(self.request.get('taskid'))
		task = Task.get_by_id(taskid)

		if use_google_auth:
			now = datetime.datetime.now(EET())
			event = gcal_service.events().get(calendarId=atividades_cal, eventId=task.eventId).execute(http=http)
			event['end'] = {
			'dateTime': now.strftime(gcal_timeformat),
			'timeZone': 'Europe/Helsinki'
			}
			updated_event = gcal_service.events().update(calendarId=atividades_cal, eventId=task.eventId,
			                                             body=event).execute(http=http)

		task.done = True
		task.datedone = datetime.datetime.now(EET())
		task.put()
		self.redirect('/?activetab=todo')


class TaskDeleter(webapp.RequestHandler):
	def post(self):
		taskid = int(self.request.get('taskid'))
		task = Task.get_by_id(taskid)
		task.delete()
		self.redirect('/?activetab=todo')


class Eversticky(webapp.RequestHandler):
	def get(self):
		self.response.headers['Content-Type'] = 'text/plain'
		tasks = db.GqlQuery("SELECT * "
		                    "FROM Task "
		                    "WHERE done = FALSE "
		                    "ORDER BY date DESC")
		logging.info('tasks %s' % tasks)
		lines = []
		for task in tasks:
			lines.append(task.text)
		self.response.out.write('\n'.join(lines))


class BillInserter(webapp.RequestHandler):
	def post(self):
		bill = Bill()
		moneystr = self.request.get('bill-money')
		moneystr = moneystr.replace(',', '.')
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
     (oauth_decorator.callback_path, oauth_decorator.callback_handler()),
     ('/statistics', ViewStatistics),
     ('/_statistics', Statistics),

     ('/insertTask', TaskInserter),
     ('/playTask', TaskPlay),
     ('/stopTask', TaskStop),
     ('/deleteTask', TaskDeleter),

     ('/insertBill', BillInserter),
     ('/deleteBill', BillDeleter),

     ('/insertWish', WishInserter),
     ('/deleteWish', WishDeleter),

     ('/eversticky', Eversticky),
     ],
  debug=True)

