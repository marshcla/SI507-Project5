## import statements
import json
import unittest
import requests_oauthlib
import pytumblr
import urllib
import requests
import webbrowser
import csv
from datetime import datetime
import tumsecret

## CACHING SETUP

DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S.%f"
DEBUG = True
CACHE_FNAME = 'cache_file.json'
CREDS_CACHE_FILE = 'creds.json'

try:
    cache_file = open(CACHE_FNAME, 'r')
    cache_json = cache_file.read()
    CACHE_DICTION = json.loads(cache_json)
    cache_file.close()
except:
    CACHE_DICTION = {}

# Load creds cache
try:
    with open(CREDS_CACHE_FILE,'r') as creds_file:
        cache_creds = creds_file.read()
        CREDS_DICTION = json.loads(cache_creds)
except:
    CREDS_DICTION = {}

def has_cache_expired(timestamp_str, expire_in_days):
    now = datetime.now()
    cache_timestamp = datetime.strptime(timestamp_str, DATETIME_FORMAT)
    delta = now - cache_timestamp
    delta_in_days = delta.days

    if delta_in_days > expire_in_days:
        return True
    else:
        return False

def get_from_cache(identifier, dictionary):
    identifier = identifier.upper()
    if identifier in dictionary:
        data_assoc_dict = dictionary[identifier]
        if has_cache_expired(data_assoc_dict['timestamp'],data_assoc_dict["expire_in_days"]):
            if DEBUG:
                print("Cache has expired for {}".format(identifier))
            del dictionary[identifier]
            data = None
        else:
            data = dictionary[identifier]['values']
    else:
        data = None
    return data

def set_in_data_cache(identifier, data, expire_in_days):
    identifier = identifier.upper()
    CACHE_DICTION[identifier] = {
        'values': data,
        'timestamp': datetime.now().strftime(DATETIME_FORMAT),
        'expire_in_days': expire_in_days
    }

    with open(CACHE_FNAME, 'w') as cache_file:
        cache_json = json.dumps(CACHE_DICTION)
        cache_file.write(cache_json)

def set_in_creds_cache(identifier, data, expire_in_days):
    identifier = identifier.upper() # make unique
    CREDS_DICTION[identifier] = {
        'values': data,
        'timestamp': datetime.now().strftime(DATETIME_FORMAT),
        'expire_in_days': expire_in_days
    }

    with open(CREDS_CACHE_FILE, 'w') as cache_file:
        cache_json = json.dumps(CREDS_DICTION)
        cache_file.write(cache_json)

## ADDITIONAL CODE for program should go here...
## Perhaps authentication setup, functions to get and process data, a class definition... etc.

# For Tumblr Oauth1:
CLIENT_KEY = tumsecret.CLIENT_KEY
CLIENT_SECRET = tumsecret.CLIENT_SECRET
AUTHORIZATION_BASE_URL = 'https://www.tumblr.com/oauth/authorize'
ACCESS_TOKEN_URL = 'https://www.tumblr.com/oauth/access_token'
REQUEST_TOKEN_URL = 'https://www.tumblr.com/oauth/request_token'
REDIRECT_URI = 'https://www.programsinformationpeople.org/runestone/oauth'
BASE_URL = 'https://api.tumblr.com/v2/'


def get_tokens(client_key=CLIENT_KEY, client_secret=CLIENT_SECRET,request_token_url=REQUEST_TOKEN_URL,base_authorization_url=AUTHORIZATION_BASE_URL,access_token_url=ACCESS_TOKEN_URL,verifier_auto=True, redirect_uri=REDIRECT_URI):
    oauth_inst = requests_oauthlib.OAuth1Session(client_key,client_secret=client_secret)

    fetch_response = oauth_inst.fetch_request_token(request_token_url)

    resource_owner_key = fetch_response.get('oauth_token')
    resource_owner_secret = fetch_response.get('oauth_token_secret')

    auth_url = oauth_inst.authorization_url(base_authorization_url)

    webbrowser.open(auth_url)

    redirect_result = redirect_uri
    oauth_resp = oauth_inst.parse_authorization_response(redirect_result)

    oauth_inst = requests_oauthlib.OAuth1Session(client_key, client_secret=client_secret, resource_owner_key=resource_owner_key, resource_owner_secret=resource_owner_secret, verifier=verifier)

    oauth_tokens = oauth_inst.fetch_access_token(access_token_url)

    resource_owner_key, resource_owner_secret = oauth_tokens.get('oauth_token'), oauth_tokens.get('oauth_token_secret')

    return client_key, client_secret, resource_owner_key, resource_owner_secret, verifier

def get_tokens_from_service(service_name_ident, expire_in_days=7):
    creds_data = get_from_cache(service_name_ident, CREDS_DICTION)
    if creds_data:
        if DEBUG:
            print("Loading creds from cache...")
            print()
    else:
        if DEBUG:
            print("Fetching fresh credentials...")
            print("Prepare to log in via browser.")
            print()
        creds_data = get_tokens()
        set_in_creds_cache(service_name_ident, creds_data, expire_in_days=expire_in_days)
    return creds_data

def get_data_from_api(blog_identifier, method="info", service_ident="Tumblr", expire_in_days=7):
    """Check in cache, if not found, load data, save in cache and then return that data"""
    request_url = "http://api.tumblr.com/v2/blog/{}.tumblr.com/{}".format(blog_identifier, method)
    data = get_from_cache(request_url, CACHE_DICTION)
    if data:
        if DEBUG:
            print("Loading from data cache: {}... data".format(request_url))
    else:
        if DEBUG:
            print("Fetching new data from {}".format(request_url))

        client_key, client_secret, resource_owner_key, resource_owner_secret, verifier = get_tokens_from_service(service_ident)

        oauth_inst = requests_oauthlib.OAuth1Session(client_key, client_secret=client_secret,resource_owner_key=resource_owner_key,resource_owner_secret=resource_owner_secret)

        resp = oauth_inst.get(request_url)

        data_str = resp.text
        data = json.loads(data_str)
        set_in_data_cache(request_url, data, expire_in_days)
    return data

tumblrs_lst = []

tumblr1 = get_data_from_api("womeninarthistory")
tumblrs_lst.append(tumblr1)

tumblr2 = get_data_from_api("mydaguerreotypeboyfriend")
tumblrs_lst.append(tumblr2)

tumblr3 = get_data_from_api("fuckyeahhistorycrushes")
tumblrs_lst.append(tumblr3)

tumblr4 = get_data_from_api("historical-nonfiction")
tumblrs_lst.append(tumblr4)

tumblr5 = get_data_from_api("caravaggista")
tumblrs_lst.append(tumblr5)

tumblr_post_lst = []

tumblr6 = get_data_from_api("womeninarthistory", "posts")
tumblr_post_lst.append(tumblr6)

tumblr7 = get_data_from_api("mydaguerreotypeboyfriend", "posts")
tumblr_post_lst.append(tumblr7)

tumblr8 = get_data_from_api("fuckyeahhistorycrushes", "posts")
tumblr_post_lst.append(tumblr8)

tumblr9 = get_data_from_api("historical-nonfiction", "posts")
tumblr_post_lst.append(tumblr9)

tumblr10 = get_data_from_api("caravaggista", "posts")
tumblr_post_lst.append(tumblr10)


class Tumblr(object):

    def __init__(self, tumblr_dict):
        self.title = tumblr_dict['response']['blog']['title']
        self.description = tumblr_dict['response']['blog']['description']
        self.posts = tumblr_dict['response']['blog']['posts']
        self.url = tumblr_dict['response']['blog']['url']

    def __str__(self):
        return "{} is a Tumblr blog.".format(self.title)

class Tumblr_Posts(object):

    def __init__(self, tumblr_post_dict):
        self.blog = tumblr_post_dict["blog_name"]
        self.post_type = tumblr_post_dict["type"]
        self.post_sum = tumblr_post_dict["summary"]
        self.post_url = tumblr_post_dict["post_url"]

tumblr_insts = []
for tumblr_dict in tumblrs_lst:
    tumblr_insts.append(Tumblr(tumblr_dict))

tumblr_posts_inst = []
for tum in tumblr_post_lst:
    try:
        for i in range(len(tum["response"]["posts"])):
            tumblr_posts_inst.append(Tumblr_Posts(tum["response"]["posts"][i]))
    except:
        pass

with open('tumblr.csv', 'w') as csvfile:
    fieldnames = ['title', 'description', 'num_posts', 'url']
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

    writer.writeheader()
    for inst in tumblr_insts:
        writer.writerow({'title': inst.title, 'description': inst.description,
                         'num_posts': inst.posts, 'url': inst.url})

with open("tum_posts.csv", "w") as csvfile:
    fieldnames = ['blog', 'post_type', 'post_summary', 'post_url']
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

    writer.writeheader()
    for post in tumblr_posts_inst:
        writer.writerow({'blog': post.blog, 'post_type': post.post_type, 'post_summary': post.post_sum,
                         'post_url': post.post_url})





## Make sure to run your code and write CSV files by the end of the program.
