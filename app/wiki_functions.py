from google.appengine.ext import db
import datetime, time
from datetime import date
import logging

# import our DB models
from models import *

def save_page(content,link):
    if content:
        parent = get_parent(link)
        if parent:
            version_number = int(get_latest_page(link).version_number) + 1
            page = Page(content=content,link=link,created=parent.created, version_number = version_number, parent = parent)
        else:
            page = Page(content=content,link=link,created=datetime.datetime.now(), version_number = 0)
        page.put()
        page_key = page.put()
        page_id = page_key.id()
        page.put()
        return [True,page]
    else:
        response = "There are errors. Please try again."
        if content == "":
            response = "Please enter some content."
        return [False, response]

def get_latest_page(pagelink):
	q = Page.all().filter('link = ', pagelink).order('-last_edited')
	return q.get()
    
def get_parent(pagelink):
	q = Page.all().filter('link = ', pagelink).filter('version_number = ',0)
	return q.get()

def count_revisions(pagelink):
    q = Page.all().filter('link = ', pagelink)
    page = q.get(keys_only=True)
    return q.count()-1
    
# Following function takes ID of latest page for pagelink and query string to determine
# 1 - if the query string return a valid page for that link
# 2 - if it does, it that page is the latest version of that page

def check_page_version(latestpage_key, version_id, pagelink):
    q = Page.get_by_id(int(version_id), parent = get_parent(pagelink)) # this fails if the ID is for the original version, as it has no parent
    if q is None:
        q = Page.get_by_id(int(version_id)) # this catches the page if the ID is for the original version
        # if q exists, we need to fetch this version of the page
    if q:
        page = q
        latest_version = 0 # false
        new_version_key = page.key()
        if new_version_key == latestpage_key:
            latest_version = 1 # true
        return [q, latest_version]