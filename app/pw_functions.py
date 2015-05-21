import re
import hashlib
import hmac
import string
from string import letters
import random
import logging

def make_salt():
    return ''.join(random.choice(string.letters) for x in xrange(5))

def make_pw_hash(name, pw, salt=None):
    if not salt:
        salt=make_salt()
    h = hashlib.sha256(name + pw + salt).hexdigest()
    return '%s|%s' % (h, salt)

def valid_pw(name, pw, h):
    salt = h.split('|')[1]
    return h == make_pw_hash(name, pw, salt)

USER_RE = re.compile(r"^[a-zA-Z0-9_-]{3,20}$")

def valid_username(username):
    return username and USER_RE.match(username)

PASS_RE = re.compile(r"^.{3,20}$")

def valid_password(password):
    return password and PASS_RE.match(password)

EMAIL_RE  = re.compile(r'^[\S]+@[\S]+\.[\S]+$')

def valid_email(email):
    return not email or EMAIL_RE.match(email)
    
def is_logged_in(cookie_val):
    if len(cookie_val) > 1:
        hash = str(cookie_val.split('|')[0]) + "|" +  str(cookie_val.split('|')[1])
        username = str(cookie_val.split('|')[2])
        password = str(cookie_val.split('|')[3])
    
        if valid_pw(username,password,hash):
            logging.info("username is" + username)
            return str(username)
        else: 
            return False
    else:
        return False