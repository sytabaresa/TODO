import json as simplejson
from google.appengine.ext import db
from google.appengine.api import users
import webapp2 as webapp
import jinja2
import os
import logging
import datetime
import calendar

jinja_environment = jinja2.Environment(
	loader=jinja2.FileSystemLoader(os.path.dirname(__file__)))

from oauth2client.appengine import OAuth2Decorator
from apiclient.discovery import build

use_google_auth = False 
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

def getFirstDayGQLstr(a_datetime):
	first_day_month = datetime.datetime(day=1, month=a_datetime.month, year=a_datetime.year)
	return first_day_month.strftime('%Y-%m-%d 00:00:00')

def getLastDayGQLstr(a_datetime):
	last_day_month = datetime.datetime(day=calendar.monthrange(a_datetime.year, a_datetime.month)[1], month=a_datetime.month, year=a_datetime.year)
	return last_day_month.strftime('%Y-%m-%d 23:59:59')	

def getSomedayPreviousMonth(a_datetime, month_offset):
	someday = a_datetime
	i = month_offset
	while i > 0:
		someday = datetime.datetime(day=1, month=someday.month, year=someday.year) - datetime.timedelta(days=1)
		i -= 1
	return someday 

def userForbidden():
	http = None
	user = None
	if use_google_auth:
		http = oauth_decorator.http()
		user = users.get_current_user()
		if user.email() not in allowed_users:
			return True
	return False

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

class MainPage(webapp.RequestHandler):
	#@oauth_decorator.oauth_required
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

		this_year = datetime.datetime.now().year
		this_month = datetime.datetime.now().month
		bills = db.GqlQuery("SELECT * "
		                    "FROM Bill "
		                    "WHERE date >= DATETIME('" + str(this_year) + "-" + str(this_month) + "-01 00:00:00') "
																								  "ORDER BY date DESC")		
		categories = db.GqlQuery("SELECT * "
		                         "FROM BillCategory "
		                         "ORDER BY display_order")

		this_month_expenses = 0
		for bill in bills:
			if bill.money < 0 and bill.date.month == datetime.datetime.now().month:
				this_month_expenses += abs(bill.money)

		user_link = None
		if use_google_auth:
			user_link = users.create_logout_url('/') if user else users.create_login_url('/')

		template_values = {
		'bills': bills,
		'categories': categories,
		'this_month_expenses': this_month_expenses,
		'user': user,
		'user_link': user_link,
		}

		template = jinja_environment.get_template('templates/index.html')
		self.response.out.write(template.render(template_values))


class ViewStatistics(webapp.RequestHandler):
	#@oauth_decorator.oauth_required
	def get(self, month_offset):
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
	
		month_offset = int(month_offset)	
		title = getSomedayPreviousMonth(datetime.datetime.now(), month_offset).strftime('%B %Y')
		template_values = {
			'title': title,
		   'expenses': getExpensesStatistics(month_offset),
			'total_earned': getTotalEarned(month_offset),
			'total_spent': getTotalSpent(month_offset),
		}
		template = jinja_environment.get_template('templates/statistics.html')
		self.response.out.write(template.render(template_values))

def getBillsOfMonth(someday_month):
	bills = db.GqlQuery("SELECT * "
                      "FROM Bill "
                      "WHERE date >= DATETIME('" +getFirstDayGQLstr(someday_month)+"') "
							 "AND date <= DATETIME('"+ getLastDayGQLstr(someday_month)+"') "
                      "ORDER BY date DESC")
	return bills

def getTotalSpent(month_offset):
	month = getSomedayPreviousMonth(datetime.datetime.now(), month_offset)
	bills = getBillsOfMonth(month)
	sum = 0
	for bill in bills:
		if bill.money < 0:
			sum += abs(bill.money)
	return sum

def getTotalEarned(month_offset):
	month = getSomedayPreviousMonth(datetime.datetime.now(), month_offset)
	bills = getBillsOfMonth(month)
	sum = 0
	for bill in bills:
		if bill.money > 0:
			sum += abs(bill.money)
	return sum

def getExpensesStatistics(month_offset):
	month = getSomedayPreviousMonth(datetime.datetime.now(), month_offset)
	categories = db.GqlQuery("SELECT * FROM BillCategory")
	bills = getBillsOfMonth(month)
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
	return data

class LoadLocalData(webapp.RequestHandler):
	def get(self):
		# In case you want to load data to local database
		BillCategory.loadCategoriesFromFile()
		Bill.loadSampleBillsFromFile()

		self.response.headers['Content-Type'] = 'application/json'
		self.response.out.write(getExpensesStatistics(0))


class EET(datetime.tzinfo):
	def utcoffset(self, dt):
		return datetime.timedelta(hours=2)

	def dst(self, dt):
		return datetime.timedelta(0)


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
		self.redirect('/')


class BillDeleter(webapp.RequestHandler):
	def post(self):
		billid = int(self.request.get('billid'))
		bill = Bill.get_by_id(billid)
		bill.delete()
		self.redirect('/')


app = webapp.WSGIApplication([
	                             ('/', MainPage),
	                             (oauth_decorator.callback_path, oauth_decorator.callback_handler()),
	                             ('/statistics/(\d+)', ViewStatistics),
	                             ('/loadlocaldata', LoadLocalData),

	                             ('/insertBill', BillInserter),
	                             ('/deleteBill', BillDeleter),

	                             ],
                             debug=True)

