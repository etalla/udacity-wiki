from google.appengine.ext import db

# DB classes
class User(db.Model):
    created = db.DateTimeProperty(auto_now_add = True)
    username = db.StringProperty(required = True)
    email = db.StringProperty(required = False)
    password = db.StringProperty(required = True)
 
class Blog(db.Model):
    created = db.DateTimeProperty(auto_now_add = True)
    title = db.StringProperty(required = True)
    content = db.TextProperty(required = True)
    link = db.StringProperty()
    
class Page(db.Model):
    created = db.DateTimeProperty(auto_now_add = False)
    content = db.TextProperty(required = True)
    link = db.StringProperty(required = True)
    last_edited = db.DateTimeProperty(auto_now_add = True)
    version_number = db.IntegerProperty(required = True)