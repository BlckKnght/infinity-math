#!/usr/bin/env python
#
# Copyright 2011 Steven Barker

import webapp2 as webapp
from google.appengine.ext.webapp import util

import home

app = webapp.WSGIApplication([('/', home.HomeHandler)], debug=True)

def main():
    util.run_wsgi_app(application)

if __name__ == '__main__':
    main()
