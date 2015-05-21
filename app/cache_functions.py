from google.appengine.ext import db
import datetime, time
from datetime import date
import logging

# import our DB models
from models import *

cache = {}
cache_time = {}

def set_cache(key, value):
    global cache
    global cache_time
    cache[key] = value
    cache_time[key] = int(time.time())
    #logging.info("wrote to cache")
    return True

def get_cacheval(key):
    global cache
    return cache.get(key)

def get_cachetime(key):
    global cache_time
    cached_time = cache_time.get(key)
    if cached_time is None:
        cached_time = int(time.time())
    return cached_time

def delete_cacheval(key):
    global cache
    global cache_time
    if key in cache:
        del cache[key]
    if key in cache_time:
        del cache_time[key]     

def flush_cache():
    global cache
    global cache_time
    cache.clear()
    cache_time.clear()

def get_cachehash(key):
    global cache
    return (get_cacheval(key), hash(repr(key)))

def cas(key, value, cas_unique):
    global cache
    if get_cachehash(key)[1] == cas_unique:
        return set_cache(key, value)
        
def top_posts():
    key = 'top'
    posts = get_cacheval(key)
    if posts is None:
        posts = db.GqlQuery("SELECT * FROM Blog ORDER BY created Desc LIMIT 10")
        posts = list(posts)
        set_cache(key, posts)
    return posts

def single_post(post_id):
    post_id = int(post_id)
    post = get_cacheval(post_id)
    if post is None:
        post = Blog.get_by_id(post_id)
        set_cache(post_id, post)
    return post

def query_age(key):
	cachetime = datetime.datetime.fromtimestamp(get_cachetime(key)).strftime('%Y-%m-%d %H:%M:%S')
	cachetime = datetime.datetime.strptime(cachetime,'%Y-%m-%d %H:%M:%S')
	now = time.strftime('%Y-%m-%d %H:%M:%S')
	now = datetime.datetime.strptime(now,'%Y-%m-%d %H:%M:%S')
	diff = now - cachetime
	return diff