#!/usr/bin/python
#
# Simple program to demonstrate retrieving a page and using BeautifulSoup to extract
# information from that page. Written for Python 2.7.
#
# By Jason Champion, License = MIT.
from bs4 import BeautifulSoup
import urllib2
import httplib
import socket
import re
import urlparse

def GetPage(url):
    """
    Takes a URL and tries to return HTML data as text.
    """
    # Process the URL and get the domain name.
    domain = urlparse.urlparse(url).netloc
    print u'URL {0} is from the domain {1}'.format(url, domain)
    if domain in [u'reallygrosscheese.com', u'badthingsfrompirates.com', u'infectedsocks.co']:
        print u'This domain is blocked.'
        return None
    # Prepare to retrieve the URL.
    print u'Retrieving {0}'.format(url)
    req = urllib2.Request(url)
    # Set our user agent before making a request.
    req.add_header('User-agent', 'Example/1.0')
    # Open the URL with a 20-second timeout.
    response = urllib2.urlopen(req, timeout=20)
    try:
        # Only read the first 64 kilobytes of HTML at most. Read more if you have the bandwidth.
        html = response.read(65536)
        # Get the URL that we retrieved. We can use that to figure out whether
        # we've been redirected (302, etc.)
        realurl = response.geturl()
        print u'Real URL is: {0}'.format(realurl)
        # Get the name of the web server that gave us the page.
        server_header = response.headers.get('server', None)
        if server_header:
            print u'Server: {0}'.format(unicode(server_header))
        # Get the content type that the server gave us for that page.
        content_type_header = response.headers.get('content-type', None)
        if content_type_header:
            print u'Content-Type: {0}'.format(unicode(content_type_header))
        # Return page data.
        return html
    except urllib2.HTTPError, e:
        print u'HTTP Error: {0}'.format(e.code)
        return None

def ParseHtml(text):
    """
    Takes a string of text, presumably HTML, and tries to extract meaningful data.
    """
    # Parse the page. BeautifulSoup is designed to handle badly-formed HTML, so
    # if we retrieved 64k of a 65k page, it'll still do reasonably well.
    soup = BeautifulSoup(html)
    # Get the page title. Limit it to 255 characters.
    if soup.title:
        print u'Title: {0}'.format(soup.title.string.strip()[0:255])
    # Get the page meta description. Limit it to 320 characters.
    description = soup.findAll(attrs = {'name': 'description'})
    if len(description) > 0:
        print u'Description: {0}'.format(description[0]['content'].strip()[0:320])
    # Find the H1 tags on the page and print the first one.
    headtags = soup.findAll('h1')
    if len(headtags) > 0:
        print u'First H1 Tag: {0}'.format(headtags[0].text.strip())
    # Get the number of style sheets for the page
    num_stylesheets = 0
    links = soup.findAll('link')
    for link in links:
        rel = link.attrs.get('rel', None)
        if rel and rel[0].lower() == u'stylesheet':
            num_stylesheets += 1
    print u'This page has {0} stylesheet(s)'.format(num_stylesheets)
    # Remove all script tags from the document tree. This makes for cleaner text.
    scripts = soup.findAll('script')
    print u'Removing {0} scripts.'.format(len(scripts))
    for script in scripts:
        script.extract()
    # Do a basic text extraction to get the words on the page. A more robust system
    # would do a lot more cleaning.
    text = ' '.join(soup.findAll(text=True))
    text = text.replace('\n', ' ')
    if text:
        # Collapse multiple spaces into a single space.
        text = re.sub('\s+', ' ', text).strip()
    print u'Page Text: {0}'.format(text)
    # Get the first 5 links on the page.
    for link in soup.find_all('a')[0:5]:
        hr = link.get('href')
        if hr:
            # We could save this link in a crawl queue or database to retrieve later.
            print u'This page links to {0}'.format(hr)

# Retrieve a test page.
url = 'https://wbsrch.com'
html = GetPage(url)
if html:
    ParseHtml(html)

