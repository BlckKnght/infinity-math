#!/usr/bin/env python
#
# Copyright 2011 Steven Barker

import os
from google.appengine.ext import webapp
from google.appengine.ext.webapp import util
from google.appengine.dist import use_library

os.environ['DJANGO_SETTINGS_MODULE'] = 'django_settings'
use_library('django', '1.2')

import home

def main():
    application = webapp.WSGIApplication([('/', home.HomeHandler)],
                                         debug=True)
    util.run_wsgi_app(application)


if __name__ == '__main__':
    main()
