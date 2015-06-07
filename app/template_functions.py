import os
import webapp2
import jinja2
import cgi  # escaping

from google.appengine.ext.webapp import template

template_dir = os.path.join(os.path.dirname(__file__) + '/../templates/')
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir))
                               
def render_str(template, **params):
    global jinja_env
    t = jinja_env.get_template(template)
    return t.render(params)