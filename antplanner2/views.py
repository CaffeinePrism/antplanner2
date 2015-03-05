from antplanner2 import app, websoc
from flask import flash, render_template, request, jsonify, json
from google.appengine.api import memcache
from google.appengine.ext import db
import logging
import os
import urllib, urllib2, json

logger = logging.getLogger(__name__)
dev_mode = 'SERVER_SOFTWARE' in os.environ and os.environ['SERVER_SOFTWARE'].startswith('Development')

@app.route('/')
def index():
    index_html = memcache.get('index')
    if not index_html:
        index_html = render_template('index.html')
        memcache.add('index', index_html, 60 * 60 * 24)
    return index_html

@app.route('/websoc/search', methods=['GET'])
def websoc_search_form():
    form_html = memcache.get('search')
    if not form_html:
        form_html = websoc.get_search()
        memcache.add('search', form_html, 60 * 60 * 24)

    return render_template('websoc/search.html', form_content=form_html)

@app.route('/websoc/search', methods=['POST'])
def websoc_search():
    key = str(request.form)
    listing_html = memcache.get(key)
    if not listing_html:
        listing_html = websoc.get_listing(request.form)
        memcache.add(key, listing_html, 60 * 60 * 24)
    return render_template('websoc/listing.html', listing=listing_html)

@app.route('/schedules/add', methods=['POST'])
def save_schedule():
    url = 'http://antplanner.appspot.com/schedules/add'
    username = request.form.get('username')
    data = request.form.get('data')
    values = {'username': username, 'data': data}
    try:
        data = urllib.urlencode(values)
        req = urllib2.Request(url, data)
        response = urllib2.urlopen(req)
        return jsonify(success=True)
    except:
        return jsonify(success=False)

@app.route('/schedule/load')
def load_schedule():
    username = request.args.get('username')
    response = urllib2.urlopen('http://antplanner.appspot.com/schedule/load?username=' + username)
    return jsonify(json.load(response))

@app.route('/test')
def qunit():
    return render_template('test.html')

#
# Jinja2 globals
#
app.jinja_env.globals['dev_mode'] = dev_mode

#
# Models
#
class Schedule(db.Model):
    data = db.TextProperty(required=True)
    modified_at = db.DateProperty(required=True, auto_now=True)
