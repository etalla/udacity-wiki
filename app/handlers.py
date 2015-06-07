import os
import datetime, time
from datetime import date
import json
import logging

#import our DB models and functions
from template_functions import *
from models import *
from cache_functions import *
from pw_functions import *
from wiki_functions import *

# Template classes   
class BaseHandler(webapp2.RequestHandler):
    def render(self, template, **kw):
        self.response.out.write(render_str(template, **kw))

    def render_str(self, template,**params):
        t=jinja_env.get_template(template)
        return t.render(params)

    def write(self, *a, **kw):
        self.response.out.write(*a, **kw)

class BlogHome(BaseHandler):
    def get(self):
        diff = query_age('top')
        username = is_logged_in(self.request.cookies.get('auth'))
        self.render('blog.html', page_title = "Your 10 latest posts", posts = top_posts(), seconds = diff.seconds, username = username)

class Welcome(BaseHandler):
    def get(self):
        username = is_logged_in(self.request.cookies.get('auth'))
        self.render('welcome.html', username = username)

class Signup(BaseHandler):
    def get(self):
        username = is_logged_in(self.request.cookies.get('auth'))
        if username:
            self.redirect('/welcome')
        else:
            self.render("signup-form.html")

    def post(self):
        have_error = False
        username_field = self.request.get('username_field')
        password = self.request.get('password')
        verify = self.request.get('verify')
        email = self.request.get('email')

        params = dict(username_field = username_field,
                      email = email)

        if not valid_username(username_field):
            params['error_username'] = "That's not a valid username."
            have_error = True

        if not valid_password(password):
            params['error_password'] = "That wasn't a valid password."
            have_error = True

        elif password != verify:
            params['error_verify'] = "Your passwords didn't match."
            have_error = True

        if not valid_email(email):
            params['error_email'] = "That's not a valid email."
            have_error = True

        if valid_username:
            q = User.all().filter('username = ', username_field)
            if q.get():
                params['error_username'] = "This username is already taken."
                have_error = True
                
        if have_error:
            self.render('signup-form.html', **params)
        else:
            password_hash = make_pw_hash(username_field,password)
            user = User(username=username_field,email=email,password=password_hash)
            user.put()
            cookievalue = password_hash + '|' + username_field + '|' + password
            self.response.headers.add_header('Set-Cookie', 'auth='+str(cookievalue)+'; Path=/')
            self.redirect('/welcome')

class Login(BaseHandler):
    def get(self):
        username = is_logged_in(self.request.cookies.get('auth'))
        if username:
            self.redirect('/welcome')
        else:
            self.render('login.html')

    def post(self):
        username_field = self.request.get('username_field')
        password = self.request.get('password')
        if username_field == "":
            self.render('login.html', error_username = "Please enter a username")
        elif password == "":
            self.render('login.html', username_field = username_field, error_password = "Please enter a password")
        else:
            q = User.all()
            q.filter("username =", username_field)
            if q.get() == None:
                self.render('login.html', username_field = username_field, error_username = "No such username exists")
            else: 
                for p in q.run(limit=1):
                    hash = p.password
                if valid_pw(username_field,password,hash):
                    cookievalue = make_pw_hash(username_field,password) + '|' + username_field + '|' + password
                    self.response.headers.add_header('Set-Cookie', 'auth='+str(cookievalue)+'; Path=/')
                    self.render('welcome.html', username = username_field)
                else:
                    self.render('login.html', username_field = username_field, password = password, error_password = "Invalid login")

class Logout(BaseHandler):
    def get(self): 
        cookievalue = ""
        self.response.headers.add_header('Set-Cookie', 'auth='+str(cookievalue)+'; Path=/')
        self.redirect(self.request.referrer)
        
class Add(BaseHandler):
    def get(self):
        username = is_logged_in(self.request.cookies.get('auth'))
        if username:
            self.render('newpost.html',page_title="New post",post_title="",post_entry="",errors="",error_class="",username=username)
        else:
            self.redirect('/signup')

    def post(self):
        post_title = self.request.get('subject')
        post_entry = self.request.get('content')
        username = is_logged_in(self.request.cookies.get('auth'))
        if post_title and post_entry:
            post = Blog(title=post_title,content=post_entry)
            post.put()
            post_key = post.put()
            post_id = post_key.id()
            post.link = 'blog/'+str(post_id)
            post.put()
            delete_cacheval('top')
            self.redirect('/blog/'+str(post_id))
        else:
            response = "There are errors. Please try again."
            if (post_title =="" and post_entry ==""):
                response = "Please enter your post's title and content."
            elif post_title == "":
                response = "Please enter a title."
            elif post_entry == "":
                response = "Please enter some content."
            self.render('newpost.html',page_title="Add a post",post_title=post_title,post_entry=post_entry,errors=response,error_class="show", username=username)

class PostPage(BaseHandler):
    def get(self, post_id):
        if ".json" in post_id:
            post = Blog.get_by_id(int(post_id.split('.json')[0]))
            post = {}
            post['subject'] = post.title
            post['created'] = post.created.strftime('%Y-%m-%d %H:%M:%S %Z')
            post['content'] = post.content
            json_data = json.dumps(post)       
            self.response.headers['Content-Type'] = 'application/json; charset=utf-8'
            self.response.write(json_data)
        else:
            username = is_logged_in(self.request.cookies.get('auth'))
            post = single_post(post_id)
            if not post:
                self.error(404)
                return
            diff = query_age(int(post_id))
            self.render("post.html", post = post, seconds = diff.seconds, username = username)

## Wiki pages handlers
class EditPage(BaseHandler):
    def get(self, pagelink="/"):
        page = get_latest_page(pagelink)
        username = is_logged_in(self.request.cookies.get('auth'))
        if page:
            version_id = self.request.get('version')
            latest_version = 1 #true by default if there is no query string 
            if version_id and version_id.isdigit() is True:  # if there is a valid-looking query string
                valid_pageversion = check_page_version(page.key(), version_id, pagelink)
                if valid_pageversion:
                    page = valid_pageversion[0]
                    latest_version = valid_pageversion[1]
            if username:
                self.render("edit_page.html",username=username,page=page, version_id=str(version_id), latest_version = latest_version, count = count_revisions(pagelink))        
            else:
                self.render("page.html",username=username,page=page, version_id=str(version_id), latest_version = latest_version, count = count_revisions(pagelink))        
        # if page doesn't exist:
        else:
            # check if it's a protected page and if so, redirect it to the page
            protected_pages = ['/blog', 
                    '/newpost',
                    '/blog/[0-9]+)',
                    '/signup',
                    '/login', 
                    '/logout',
                    '/welcome',
                    '/blog.json',
                    '/.json',
                    '/flush',
                    '/wikipages'
            ]
            if pagelink in protected_pages:
                logging.info(pagelink)
                self.redirect(pagelink)
            else:
                if username:
                    self.render("newpage.html", username=username)
                else:
                    self.redirect('/login')

    def post(self, pagelink):
        username = is_logged_in(self.request.cookies.get('auth'))
        content = self.request.get('content')
        response = save_page(content,pagelink)
        if response[0] is True:
            self.redirect(pagelink)
        else:
            self.render('newpage.html',
            page_entry=content,
            errors = response[1],error_class="show", username=username)

class IndexHistory(BaseHandler):
    def get(self):
        username = is_logged_in(self.request.cookies.get('auth'))
        self.render('index.html', username = username)
    
class PageHistory(BaseHandler):
    def get(self, pagelink):
        username = is_logged_in(self.request.cookies.get('auth'))
        q = Page.all().filter('link = ', pagelink).order('-last_edited')
        page = q.get()
        versions = list(q.fetch(limit=30))
        count = count_revisions(pagelink)
        link = pagelink
        if page is None:
            self.redirect("/_edit"+pagelink)
        else:
            created = get_latest_page(pagelink).created
            self.render("page-history.html", link = link, count = count, versions=versions, username=username,created=created)

class WikiPage(BaseHandler):
    def get(self, pagelink="/"):
        page = get_latest_page(pagelink)
        if page is None:
            self.redirect("/_edit"+pagelink)
        else:
            username = is_logged_in(self.request.cookies.get('auth'))
            version_id = self.request.get('version')
            latest_version = 1 #true by default if there is no query string
            version_key = page.key()
            if version_id and version_id.isdigit() is True: # if there is a valid-looking query string
                valid_pageversion = check_page_version(page.key(), version_id, pagelink)
                if valid_pageversion:
                    page = valid_pageversion[0]
                    latest_version = valid_pageversion[1]
            self.render("page.html", page=page, username=username, version_id = str(version_id), latest_version = latest_version, count = count_revisions(pagelink))

    def post(self, pagelink):
        username = is_logged_in(self.request.cookies.get('auth'))
        content = self.request.get('content')
        response = save_page(content,pagelink)
        if response[0] is True:
            self.render('page.html', page=response[1], username=username)
        else:
            self.render('newpage.html',
            page_entry=content,
            errors = response[1],error_class="show", username=username)

class Wikipages(BaseHandler):
    def get(self):
        username = is_logged_in(self.request.cookies.get('auth'))
        q = Page.all().filter('version_number = ', 0).order('-created')
        parents = list(q.fetch(limit=30))
        latest_pages = []
        for parent in parents:
            latest_pages.append(get_latest_page(parent.link))
        self.render('wikipages.html', latest_pages = latest_pages, username=username)
#Json
class BlogJson(BaseHandler):
    def get(self):
        posts = Blog.all()
        posts.order("created")
        post_dict = []
        for post in posts.run():
            newpost = {}
            newpost['subject'] = post.title
            newpost['created'] = post.created.strftime('%Y-%m-%d %H:%M:%S %Z')
            newpost['content'] = post.content
            post_dict.append(newpost)
        json_data = json.dumps(post_dict)
        self.response.headers['Content-Type'] = 'application/json; charset=utf-8'
        self.response.write(json_data)
#Empty cache
class Flush(BaseHandler):
    def get(self):
        flush_cache()
        self.redirect('/blog')