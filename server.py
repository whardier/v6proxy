#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import os
import sys

import pprint

import time
import datetime

import tornado.httpserver
import tornado.ioloop
import tornado.web
import tornado.process
import tornado.options
import tornado.log

import json

import motor
import pymongo

import scrypt

from tornado.options import options
from tornado.options import define

import path

_ = lambda s: s

## ┏━┓┏━┓╺┳╸╻┏━┓┏┓╻┏━┓
## ┃ ┃┣━┛ ┃ ┃┃ ┃┃┗┫┗━┓
## ┗━┛╹   ╹ ╹┗━┛╹ ╹┗━┛

def config_callback(config_path):
    options.parse_config_file(path.path(config_path).expand().abspath(), final=False)

define("config", type=str, help="Path to config file", callback=config_callback, group='Config file')

define('debug', default=False, help='Debug', type=bool, group='Application')
define('scrypt_max_time', default=0.5, help='scrypt encode/decode max time', type=float, group='Application')

define('cookie_secret', type=str, group='Cookies')
define('cookie_domain', type=str, group='Cookies')

define('listen_port', default=8000, help='Listen Port', type=int, group='HTTP Server')
define('listen_host', default='localhost', help='Listen Host', type=str, group='HTTP Server')

define('mongodb_uri', default='mongodb://localhost:27017/v6proxy', type=str, group='MongoDB')

define('page_title_prefix', type=str, default='v6proxy', group='Global Information')
define('page_copyright', type=str, default='2014 Brute Technologies', group='Global Information')

## ┏┓ ┏━┓┏━┓┏━╸╻ ╻┏━┓┏┓╻╺┳┓╻  ┏━╸┏━┓
## ┣┻┓┣━┫┗━┓┣╸ ┣━┫┣━┫┃┗┫ ┃┃┃  ┣╸ ┣┳┛
## ┗━┛╹ ╹┗━┛┗━╸╹ ╹╹ ╹╹ ╹╺┻┛┗━╸┗━╸╹┗╸

class BaseHandler(tornado.web.RequestHandler):
    def initialize(self, **kwargs):
        super(BaseHandler, self).initialize(**kwargs)

        self.kwargs = kwargs

        self.motor_client = self.settings['motor_client']
        self.motor_db = self.motor_client.get_default_database()

    def get_current_user(self):
        return 'get_current_user' 
        
    def get_template_namespace(self):
        #Set default template variables
        namespace = super(BaseHandler, self).get_template_namespace()
        namespace.update({
            'page_copyright': self.settings.get('page_copyright'),
            'page_title_prefix': self.settings.get('page_title_prefix'),
            'page_title': '',
        })

        return namespace

## ┏━┓┏━┓┏━╸┏━╸┏━╸┏━┓┏━┓┏━┓┏━┓╻ ╻┏━┓┏┓╻╺┳┓╻  ┏━╸┏━┓
## ┣━┛┣━┫┃╺┓┣╸ ┣╸ ┣┳┛┣┳┛┃ ┃┣┳┛┣━┫┣━┫┃┗┫ ┃┃┃  ┣╸ ┣┳┛
## ╹  ╹ ╹┗━┛┗━╸┗━╸╹┗╸╹┗╸┗━┛╹┗╸╹ ╹╹ ╹╹ ╹╺┻┛┗━╸┗━╸╹┗╸

class PageErrorHandler(BaseHandler):
    def get(self, *args, **kwargs):
        self.send_error(self.kwargs['error'])

    def post(self, *args, **kwargs):
        self.send_error(self.kwargs['error'])

## ┏━┓╺┳╸╻ ╻┏┓ ╻ ╻┏━┓┏┓╻╺┳┓╻  ┏━╸┏━┓
## ┗━┓ ┃ ┃ ┃┣┻┓┣━┫┣━┫┃┗┫ ┃┃┃  ┣╸ ┣┳┛
## ┗━┛ ╹ ┗━┛┗━┛╹ ╹╹ ╹╹ ╹╺┻┛┗━╸┗━╸╹┗╸

class StubHandler(BaseHandler):
    def check_xsrf_cookie(self, *args, **kwargs):
        pass

    def get(self, *args, **kwargs):
        self.write(dict(self.request.headers))

    def head(self, *args, **kwargs):
        self.write('')

    def post(self, *args, **kwargs):
        self.write(self.request.body)

    def patch(self, *args, **kwargs):
        self.write('')

    def delete(self, *args, **kwargs):
        self.write('')

    def options(self, *args, **kwargs):
        self.write('')

## ╻ ╻┏━┓┏┳┓┏━╸┏━┓┏━┓┏━╸┏━╸╻ ╻┏━┓┏┓╻╺┳┓╻  ┏━╸┏━┓
## ┣━┫┃ ┃┃┃┃┣╸ ┣━┛┣━┫┃╺┓┣╸ ┣━┫┣━┫┃┗┫ ┃┃┃  ┣╸ ┣┳┛
## ╹ ╹┗━┛╹ ╹┗━╸╹  ╹ ╹┗━┛┗━╸╹ ╹╹ ╹╹ ╹╺┻┛┗━╸┗━╸╹┗╸

class HomePageHandler(BaseHandler):

    def get(self, **kwargs):
        self.render('home.html.tpl', page_title=_('Home'))

## ╺┳┓┏━┓┏┓╻┏━┓╺┳╸╻┏━┓┏┓╻┏━┓┏━┓┏━╸┏━╸╻ ╻┏━┓┏┓╻╺┳┓╻  ┏━╸┏━┓
##  ┃┃┃ ┃┃┗┫┣━┫ ┃ ┃┃ ┃┃┗┫┣━┛┣━┫┃╺┓┣╸ ┣━┫┣━┫┃┗┫ ┃┃┃  ┣╸ ┣┳┛
## ╺┻┛┗━┛╹ ╹╹ ╹ ╹ ╹┗━┛╹ ╹╹  ╹ ╹┗━┛┗━╸╹ ╹╹ ╹╹ ╹╺┻┛┗━╸┗━╸╹┗╸

class DonationPageHandler(BaseHandler):

    def get(self, **kwargs):
        self.render('donation.html.tpl', page_title=_('Donation'))

class FAQPageHandler(BaseHandler):

    def get(self, **kwargs):
        self.render('faq.html.tpl', page_title=_('F.A.Q.'))

class StatusPageHandler(BaseHandler):

    def get(self, **kwargs):
        self.render('status.html.tpl', page_title=_('Status'))

class IPv6PageHandler(BaseHandler):

    def get(self, **kwargs):
        self.render('ipv6.html.tpl', page_title=_('IPv6'))

class SSLPageHandler(BaseHandler):

    def get(self, **kwargs):
        self.render('ssl.html.tpl', page_title=_('SSL'))

## ┏━┓┏━╸┏━┓╻ ╻┏━╸┏━┓
## ┗━┓┣╸ ┣┳┛┃┏┛┣╸ ┣┳┛
## ┗━┛┗━╸╹┗╸┗┛ ┗━╸╹┗╸

def main():

    tornado.options.parse_command_line()

    ## ┏━┓┏━╸╺┳╸╺┳╸╻┏┓╻┏━╸┏━┓
    ## ┗━┓┣╸  ┃  ┃ ┃┃┗┫┃╺┓┗━┓
    ## ┗━┛┗━╸ ╹  ╹ ╹╹ ╹┗━┛┗━┛

    code_path = path.path(__file__).parent
    static_path = code_path.joinpath('static')
    template_path = code_path.joinpath('templates')
    support_path = code_path.joinpath('support')

    handlers = [
        ## Static File Serving
        #tornado.web.url(r'/static/(css/.*)', tornado.web.StaticFileHandler, {'path': static_path}),
        #tornado.web.url(r'/static/(ico/.*)', tornado.web.StaticFileHandler, {'path': static_path}),
        #tornado.web.url(r'/static/(img/.*)', tornado.web.StaticFileHandler, {'path': static_path}),
        #tornado.web.url(r'/static/(js/.*)', tornado.web.StaticFileHandler, {'path': static_path}),
        ## OneAll
        #tornado.web.url(r'/oneall/callback', testrunonline.oneall.handlers.OneAllCallbackHandler, name='auth+oneall+callback'),
        ## Misc
        tornado.web.url(r'/__stub__$', StubHandler),
        ## FAQ
        tornado.web.url(r'/faq', FAQPageHandler, name='faq'),
        ## Status
        tornado.web.url(r'/status', StatusPageHandler, name='status'),
        ## IPv6
        tornado.web.url(r'/ipv6', IPv6PageHandler, name='ipv6'),
        ## SSL
        tornado.web.url(r'/ssl', SSLPageHandler, name='ssl'),
        ## Donation
        tornado.web.url(r'/donation', DonationPageHandler, name='donation'),
        ## Home
        tornado.web.url(r'/', HomePageHandler, name='home'),
    ]

    motor_client = motor.MotorClient(options.mongodb_uri, tz_aware=True, read_preference=pymongo.read_preferences.ReadPreference.NEAREST)

    settings = dict(
        login_url = '/login',
        logout_url = '/logout',
        register_url = '/register',
        static_path = static_path,
        template_path = template_path,
        support_path = support_path,
        xsrf_cookies = True,
        motor_client = motor_client,
        **options.as_dict()
    )

    tornado.log.gen_log.debug(pprint.pformat(settings))

    ## ┏━┓┏━┓┏━┓╻  ╻┏━╸┏━┓╺┳╸╻┏━┓┏┓╻
    ## ┣━┫┣━┛┣━┛┃  ┃┃  ┣━┫ ┃ ┃┃ ┃┃┗┫
    ## ╹ ╹╹  ╹  ┗━╸╹┗━╸╹ ╹ ╹ ╹┗━┛╹ ╹

    application = tornado.web.Application(handlers=handlers, **settings)

    http_server = tornado.httpserver.HTTPServer(application, xheaders=True)

    http_server.listen(options.listen_port, address=options.listen_host)

    loop = tornado.ioloop.IOLoop.instance()

    try:
        loop_status = loop.start()
    except KeyboardInterrupt:
        loop_status = loop.stop()

    return loop_status

## ┏┳┓┏━┓╻┏┓╻
## ┃┃┃┣━┫┃┃┗┫
## ╹ ╹╹ ╹╹╹ ╹

if __name__ == '__main__':
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        pass
