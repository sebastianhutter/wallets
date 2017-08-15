#!/usr/bin/env python

from bottle import Bottle, route, template, request

class Webservice(object):
    """docstring for Webservice"""
    def __init__(self):
        
        self.app = Bottle()

        self.app.route('/', method='GET', callback=self.overview)


    def overview(self):
        return "hello world"


    def run(self):
        Bottle.run(self.app, host='0.0.0.0', port=65000)