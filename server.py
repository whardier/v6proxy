#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import os
import sys

import pprint

import time
import datetime

import tornado.options

import tornado.ioloop
import tornado.log

import tornado.web

import tornado.httpserver
import tornado.httpclient

import urllib.parse

import json

import motor
import pymongo

import path

from tornado.options import options
from tornado.options import define

from Crypto.Cipher import AES
import base64

_ = lambda s: s

TXT_INVALIDATION_TIMEOUT = 86400 * 30 #30 days
ACTIVATION_INVALIDATION_TIMEOUT = 86400 * 60 #60 days

SUBDOMAIN_BLACKLIST = [
    "www",
]

## ┏━┓┏━┓╺┳╸╻┏━┓┏┓╻┏━┓
## ┃ ┃┣━┛ ┃ ┃┃ ┃┃┗┫┗━┓
## ┗━┛╹   ╹ ╹┗━┛╹ ╹┗━┛

def config_callback(config_path):
    options.parse_config_file(path.path(config_path).expand().abspath(), final=False)

define('config', type=str, help='Path to config file', callback=config_callback, group='Config file')

define('debug', default=False, help='Debug', type=bool, group='Application')
define('scrypt_max_time', default=0.5, help='scrypt encode/decode max time', type=float, group='Application')

define('encryption_secret', type=str, group='Encryption')

define('cookie_secret', type=str, group='Cookies')
define('cookie_domain', type=str, group='Cookies')

define('mandrill_api_key', type=str, group='Mandrill API')

define('cloudflare_api_key', type=str, group='CloudFlare API')
define('cloudflare_api_email', type=str, group='CloudFlare API')

define('listen_port', default=8000, help='Listen Port', type=int, group='HTTP Server')
define('listen_host', default='localhost', help='Listen Host', type=str, group='HTTP Server')

define('mongodb_uri', default='mongodb://localhost:27017/v6proxy', type=str, group='MongoDB')

define('page_title_prefix', type=str, default='v6proxy', group='Global Information')
define('page_copyright', type=str, default='2014 Brute Technologies', group='Global Information')

## ┏┓ ┏━┓┏━┓┏━╸╻ ╻┏━┓┏┓╻╺┳┓╻  ┏━╸┏━┓
## ┣┻┓┣━┫┗━┓┣╸ ┣━┫┣━┫┃┗┫ ┃┃┃  ┣╸ ┣┳┛
## ┗━┛╹ ╹┗━┛┗━╸╹ ╹╹ ╹╹ ╹╺┻┛┗━╸┗━╸╹┗╸

class BaseHandler(tornado.web.RequestHandler):

    ## For encryption

    BLOCK_SIZE = 32
    PADDING = '\0'

    def initialize(self, *args, **kwargs):
        super(BaseHandler, self).initialize(*args, **kwargs)

        self.kwargs = kwargs

        self.motor_client = self.settings['motor_client']
        self.motor_db = self.motor_client.get_default_database()

        self.cipher = AES.new(self.settings['encryption_secret'])

    ## For encryption

    def _pad(self, value):
        return value + (self.BLOCK_SIZE - len(value) % self.BLOCK_SIZE) * self.PADDING

    def _encrypt(self, content):
        return base64.urlsafe_b64encode(self.cipher.encrypt(self._pad(content))).decode('utf-8')

    def _decrypt(self, encrypted_payload):
        return self.cipher.decrypt(base64.urlsafe_b64decode(encrypted_payload.encode('utf-8'))).decode('utf-8').rstrip(self.PADDING)

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

    @tornado.gen.coroutine
    def cloudflare_rec_load_all(self, domain, offset):
        http_client = tornado.httpclient.AsyncHTTPClient()

        response = yield http_client.fetch('https://www.cloudflare.com/api_json.html',
            method='POST',
            body=urllib.parse.urlencode(
                {
                    'a': 'rec_load_all',
                    'tkn': self.settings['cloudflare_api_key'],
                    'email': self.settings['cloudflare_api_email'],
                    'z': domain,
                    'o': offset,
                }
            )
        )

        rec_load_all_response_content = json.loads(response.body.decode('utf-8'))

        if rec_load_all_response_content.get('result') == 'success':
            return rec_load_all_response_content['response']['recs']['objs'], rec_load_all_response_content['response']['recs']['has_more'], offset + rec_load_all_response_content['response']['recs']['count']

    @tornado.gen.coroutine
    def cloudflare_rec_new(self, record_type, content, subdomain, domain):
        http_client = tornado.httpclient.AsyncHTTPClient()

        response = yield http_client.fetch('https://www.cloudflare.com/api_json.html',
            method='POST',
            body=urllib.parse.urlencode(
                {
                    'a': 'rec_new',
                    'tkn': self.settings['cloudflare_api_key'],
                    'email': self.settings['cloudflare_api_email'],
                    'z': domain,
                    'name': subdomain,
                    'ttl': 1,
                    'type': record_type,
                    'content': content,
                }
            )
        )

        return json.loads(response.body.decode('utf-8'))

    @tornado.gen.coroutine
    def cloudflare_rec_delete(self, domain, id):
        http_client = tornado.httpclient.AsyncHTTPClient()

        response = yield http_client.fetch('https://www.cloudflare.com/api_json.html',
            method='POST',
            body=urllib.parse.urlencode(
                {
                    'a': 'rec_delete',
                    'tkn': self.settings['cloudflare_api_key'],
                    'email': self.settings['cloudflare_api_email'],
                    'z': domain,
                    'id': id,
                }
            )
        )

        return json.loads(response.body.decode('utf-8'))

    @tornado.gen.coroutine
    def cloudflare_rec_edit_enable_proxy(self, record_type, content, subdomain, domain, id):
        http_client = tornado.httpclient.AsyncHTTPClient()

        response = yield http_client.fetch('https://www.cloudflare.com/api_json.html',
            method='POST',
            body=urllib.parse.urlencode(
                {
                    'a': 'rec_edit',
                    'tkn': self.settings['cloudflare_api_key'],
                    'email': self.settings['cloudflare_api_email'],
                    'z': domain,
                    'name': subdomain,
                    'ttl': 1,
                    'type': record_type,
                    'content': content,
                    'service_mode': 1,
                    'id': id,
                }
            )
        )

        return json.loads(response.body.decode('utf-8'))

    @tornado.gen.coroutine
    def add_txt_record_from_request_content(self, request_content):

        rec_load_all_offset = 0
        rec_load_all_has_more = True

        subdomain = request_content['subdomain']
        domain = request_content['domain']

        response = yield self.cloudflare_rec_new('TXT', json.dumps(request_content, sort_keys=True), subdomain, domain)

        return response

    @tornado.gen.coroutine
    def add_aaaa_record_from_request_content(self, request_content, start='', end='', proxy=False):

        rec_load_all_offset = 0
        rec_load_all_has_more = True

        address = request_content['address']
        subdomain = start + request_content['subdomain'] + end
        domain = request_content['domain']

        while rec_load_all_has_more:
            (records, rec_load_all_has_more, rec_load_all_offset) = yield self.cloudflare_rec_load_all(domain, rec_load_all_offset)

            for record in records:

                if record['type'] == 'AAAA' and record['name'] == subdomain + '.' + domain:
                    response = yield self.cloudflare_rec_delete(domain, record['rec_id'])

        response = yield self.cloudflare_rec_new('AAAA', address, subdomain, domain)

        id = response['response']['rec']['obj']['rec_id']

        if proxy:
            edit_response = yield self.cloudflare_rec_edit_enable_proxy('AAAA', address, subdomain, domain, id)

        return response

    @tornado.gen.coroutine
    def find_latest_subdomain_request_content(self, subdomain, domain):
        http_client = tornado.httpclient.AsyncHTTPClient()

        latest_request_content = None

        rec_load_all_offset = 0
        rec_load_all_has_more = True

        while rec_load_all_has_more:
            (records, rec_load_all_has_more, rec_load_all_offset) = yield self.cloudflare_rec_load_all(domain, rec_load_all_offset)

            for record in records:

                if record['type'] == 'TXT' and record['name'] == subdomain + '.' + domain:
                    request_content_json = record['content']
                    request_content = json.loads(request_content_json)

                    if not latest_request_content:
                        latest_request_content = request_content
                    elif request_content['ts'] > latest_request_content['ts'] + TXT_INVALIDATION_TIMEOUT:
                        latest_request_content = request_content

        return latest_request_content

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

    def get(self, *args, **kwargs):
        self.render('home.html.tpl', page_title=_('Home'))

## ╺┳┓┏━┓┏┓╻┏━┓╺┳╸╻┏━┓┏┓╻┏━┓┏━┓┏━╸┏━╸╻ ╻┏━┓┏┓╻╺┳┓╻  ┏━╸┏━┓
##  ┃┃┃ ┃┃┗┫┣━┫ ┃ ┃┃ ┃┃┗┫┣━┛┣━┫┃╺┓┣╸ ┣━┫┣━┫┃┗┫ ┃┃┃  ┣╸ ┣┳┛
## ╺┻┛┗━┛╹ ╹╹ ╹ ╹ ╹┗━┛╹ ╹╹  ╹ ╹┗━┛┗━╸╹ ╹╹ ╹╹ ╹╺┻┛┗━╸┗━╸╹┗╸

class DonationPageHandler(BaseHandler):

    def get(self, *args, **kwargs):
        self.render('donation.html.tpl', page_title=_('Donation'))

## ┏━╸┏━┓┏━┓┏━┓┏━┓┏━╸┏━╸╻ ╻┏━┓┏┓╻╺┳┓╻  ┏━╸┏━┓
## ┣╸ ┣━┫┃┓┃┣━┛┣━┫┃╺┓┣╸ ┣━┫┣━┫┃┗┫ ┃┃┃  ┣╸ ┣┳┛
## ╹  ╹ ╹┗┻┛╹  ╹ ╹┗━┛┗━╸╹ ╹╹ ╹╹ ╹╺┻┛┗━╸┗━╸╹┗╸

class FAQPageHandler(BaseHandler):

    def get(self, *args, **kwargs):
        self.render('faq.html.tpl', page_title=_('F.A.Q.'))

## ┏━┓╺┳╸┏━┓╺┳╸╻ ╻┏━┓┏━┓┏━┓┏━╸┏━╸╻ ╻┏━┓┏┓╻╺┳┓╻  ┏━╸┏━┓
## ┗━┓ ┃ ┣━┫ ┃ ┃ ┃┗━┓┣━┛┣━┫┃╺┓┣╸ ┣━┫┣━┫┃┗┫ ┃┃┃  ┣╸ ┣┳┛
## ┗━┛ ╹ ╹ ╹ ╹ ┗━┛┗━┛╹  ╹ ╹┗━┛┗━╸╹ ╹╹ ╹╹ ╹╺┻┛┗━╸┗━╸╹┗╸

class StatusPageHandler(BaseHandler):

    def get(self, *args, **kwargs):
        self.render('status.html.tpl', page_title=_('Status'))

## ╻┏━┓╻ ╻┏━┓┏━┓┏━┓┏━╸┏━╸╻ ╻┏━┓┏┓╻╺┳┓╻  ┏━╸┏━┓
## ┃┣━┛┃┏┛┣━┓┣━┛┣━┫┃╺┓┣╸ ┣━┫┣━┫┃┗┫ ┃┃┃  ┣╸ ┣┳┛
## ╹╹  ┗┛ ┗━┛╹  ╹ ╹┗━┛┗━╸╹ ╹╹ ╹╹ ╹╺┻┛┗━╸┗━╸╹┗╸

class IPv6PageHandler(BaseHandler):

    def get(self, *args, **kwargs):
        self.render('ipv6.html.tpl', page_title=_('IPv6'))

## ┏━┓┏━┓╻  ┏━┓┏━┓┏━╸┏━╸╻ ╻┏━┓┏┓╻╺┳┓╻  ┏━╸┏━┓
## ┗━┓┗━┓┃  ┣━┛┣━┫┃╺┓┣╸ ┣━┫┣━┫┃┗┫ ┃┃┃  ┣╸ ┣┳┛
## ┗━┛┗━┛┗━╸╹  ╹ ╹┗━┛┗━╸╹ ╹╹ ╹╹ ╹╺┻┛┗━╸┗━╸╹┗╸

class SSLPageHandler(BaseHandler):

    def get(self, *args, **kwargs):
        self.render('ssl.html.tpl', page_title=_('SSL'))

## ┏━┓╻ ╻┏┓ ╺┳┓┏━┓┏┳┓┏━┓╻┏┓╻┏━┓┏━╸┏━╸╻┏━┓╺┳╸┏━┓┏━┓╺┳╸╻┏━┓┏┓╻╻ ╻┏━┓┏┓╻╺┳┓╻  ┏━╸┏━┓
## ┗━┓┃ ┃┣┻┓ ┃┃┃ ┃┃┃┃┣━┫┃┃┗┫┣┳┛┣╸ ┃╺┓┃┗━┓ ┃ ┣┳┛┣━┫ ┃ ┃┃ ┃┃┗┫┣━┫┣━┫┃┗┫ ┃┃┃  ┣╸ ┣┳┛
## ┗━┛┗━┛┗━┛╺┻┛┗━┛╹ ╹╹ ╹╹╹ ╹╹┗╸┗━╸┗━┛╹┗━┛ ╹ ╹┗╸╹ ╹ ╹ ╹┗━┛╹ ╹╹ ╹╹ ╹╹ ╹╺┻┛┗━╸┗━╸╹┗╸

## Post/Redirect/Get adds encrypted request

class SubdomainRegistrationHandler(BaseHandler):

    @tornado.gen.coroutine
    def get(self, encrypted_payload, *args, **kwargs):

        payload = json.loads(self._decrypt(encrypted_payload))
        request_content = payload['content']
        ts = payload['ts']

        latest_request_content = yield self.find_latest_subdomain_request_content(request_content['subdomain'], request_content['domain'])

        if (not latest_request_content or request_content['ts'] > latest_request_content['ts'] + TXT_INVALIDATION_TIMEOUT) and request_content['subdomain'] not in SUBDOMAIN_BLACKLIST:
            #well.. we're the first or the dead last.  Lets do an encrypted request token

            payload_json = json.dumps(
                {
                    'ts': time.time(),
                    'content': request_content,
                }, sort_keys=True
            )

            encrypted_payload = self._encrypt(payload_json)

            #oversimplified for now.  Could lead to issues later on
            activation_url = self.request.protocol + '://' + self.request.host + self.reverse_url('subdomain/activation/encrypted_payload', encrypted_payload)

            http_client = tornado.httpclient.AsyncHTTPClient()

            response = yield http_client.fetch('https://mandrillapp.com/api/1.0/messages/send.json',
                method='POST',
                body=json.dumps(
                    {
                        'key': self.settings['mandrill_api_key'],
                        'message': {
                            'html': '<p>Here is your <a href="' + activation_url + '">activation link</a></p>',
                            'text': 'Here is your activation link - ' + activation_url,
                            'subject': 'Activation Link',
                            'from_email': 'spencersr@v6proxy.com',
                            'from_name': 'Shane R. Spencer (v6proxy)',
                            'to': [
                                {
                                    'email': request_content['email'],
                                    'type': 'to'
                                }
                            ],
                            'bcc_address': 'spencersr@brutetech.com',
                            'subaccount': 'v6proxy',
                        },
                        'async': False,
                    }
                )
            )

            print(response.body)

            status = 'email-sent'
        else:
            status = 'not-latest-or-in-time'

        self.render('subdomain.registration.html.tpl', page_title=_('Registration Status'), status=status, latest_request_content=latest_request_content)

    def post(self, *args, **kwargs):

        payload_json = json.dumps(
            {
                'ts': time.time(),
                'content': {
                    'ts': time.time(),
                    'email': self.get_argument('email'),
                    'address': self.get_argument('address'),
                    'subdomain': self.get_argument('subdomain'),
                    'domain': self.get_argument('domain'),
                    'direct': self.get_argument('direct', 'off'),
                    'wildcard': self.get_argument('wildcard', 'off'),
                },
            }, sort_keys=True ### SORTING IS VERT IMPORTANT
        )

        encrypted_payload = self._encrypt(payload_json)
        self.redirect(self.reverse_url('subdomain/registration/encrypted_payload', encrypted_payload))

## ┏━┓╻ ╻┏┓ ╺┳┓┏━┓┏┳┓┏━┓╻┏┓╻┏━┓┏━╸╺┳╸╻╻ ╻┏━┓╺┳╸╻┏━┓┏┓╻╻ ╻┏━┓┏┓╻╺┳┓╻  ┏━╸┏━┓
## ┗━┓┃ ┃┣┻┓ ┃┃┃ ┃┃┃┃┣━┫┃┃┗┫┣━┫┃   ┃ ┃┃┏┛┣━┫ ┃ ┃┃ ┃┃┗┫┣━┫┣━┫┃┗┫ ┃┃┃  ┣╸ ┣┳┛
## ┗━┛┗━┛┗━┛╺┻┛┗━┛╹ ╹╹ ╹╹╹ ╹╹ ╹┗━╸ ╹ ╹┗┛ ╹ ╹ ╹ ╹┗━┛╹ ╹╹ ╹╹ ╹╹ ╹╺┻┛┗━╸┗━╸╹┗╸

class SubdomainActivationHandler(BaseHandler):

    @tornado.gen.coroutine
    def get(self, encrypted_payload, *args, **kwargs):

        payload = json.loads(self._decrypt(encrypted_payload))
        request_content = payload['content']
        ts = payload['ts']

        latest_request_content = yield self.find_latest_subdomain_request_content(request_content['subdomain'], request_content['domain'])

        if not latest_request_content or request_content['ts'] > latest_request_content['ts'] + TXT_INVALIDATION_TIMEOUT:
            #well.. we're the first or the dead last still!.. Lets give it a go and hope there are no races!

            yield self.add_txt_record_from_request_content(request_content)
            yield self.add_aaaa_record_from_request_content(request_content, proxy=True)
            if request_content['direct'] == 'on':
                yield self.add_aaaa_record_from_request_content(request_content, end='.direct')
            if request_content['wildcard'] == 'on':
                yield self.add_aaaa_record_from_request_content(request_content, start='*.', end='.wildcard')

            status = 'ok'
        else:
            status = 'error'

        self.render('subdomain.activation.html.tpl', page_title=_('Registration Activation'), status=status, latest_request_content=latest_request_content)


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
        ## Subdomain Registration (form)
        tornado.web.url(r'/subdomain/registration', SubdomainRegistrationHandler, name='subdomain/registration'),
        tornado.web.url(r'/subdomain/registration/(.*)', SubdomainRegistrationHandler, name='subdomain/registration/encrypted_payload'),
        ## Subdomain Activation (encoded URL)
        tornado.web.url(r'/subdomain/activation/(.*)', SubdomainActivationHandler, name='subdomain/activation/encrypted_payload'),
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
