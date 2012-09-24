from google.appengine.ext import webapp, db
from google.appengine.api import users
import jinja2
import os
import datetime

jinja_environment = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)))

class Task(db.Model):
    """Something to do"""
    text = db.StringProperty()
    date = db.DateTimeProperty(auto_now_add=True)

def tasklist_key(tasklist_name=None):
    """Constructs a Datastore key for a Tasklist entity with tasklist_name."""
    return db.Key.from_path('Tasklist', tasklist_name or 'default_tasklist')

class MainPage(webapp.RequestHandler):
    def get(self):
        tasklist_name=self.request.get('tasklist_name')
        tasks = db.GqlQuery("SELECT * "
                     "FROM Task  "
                     "WHERE ANCESTOR IS :1 "
                     "ORDER BY date DESC LIMIT 10",
                tasklist_key(tasklist_name))

        template_values = {
            'age': 25,
            'tasks': tasks,
        }

        template = jinja_environment.get_template('templates/index.html')
        self.response.out.write(template.render(template_values))

class Inserter(webapp.RequestHandler):
    def post(self):
        tasklist_name = self.request.get('tasklist_name')
        task = Task(parent=tasklist_key(tasklist_name))
        task.text = self.request.get('tasktext')
        task.put()
        self.redirect('/')

class Deleter(webapp.RequestHandler):
    def post(self):
        taskid = int(self.request.get('taskid'))
        task = Task.get_by_id(taskid)
        task.delete()
        self.redirect('/')

app = webapp.WSGIApplication([
    ('/', MainPage),
    ('/insertTask', Inserter),
    ('/deleteTask', Deleter),
    ],
    debug=True)

