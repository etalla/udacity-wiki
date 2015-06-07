import wsgiref.handlers
import webapp2
import jinja2
import re

# Import our handlers
from app.handlers import *

PAGE_RE = r'(/(?:[a-zA-Z0-9_-]+/?)*)'

app = webapp2.WSGIApplication([
                            ('/blog', BlogHome),
                            ('/', WikiPage),
                            ('/newpost',Add),
                            ('/blog/([0-9]+)', PostPage),
                            ('/signup', Signup),
                            ('/login', Login),
                            ('/logout', Logout),
                            ('/welcome', Welcome),
                            ('/blog.json', BlogJson),
                            ('/.json', BlogJson),
                            ('/flush', Flush),
                            ('/wikipages', Wikipages),
                            ('/_edit' + PAGE_RE, EditPage),
                            ('/_history', IndexHistory),
                            ('/_history' + PAGE_RE, PageHistory),
                            (PAGE_RE, WikiPage),
                            ],
                            debug=True)
                            
def main():
  wsgiref.handlers.CGIHandler().run(application)