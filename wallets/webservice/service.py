#!/usr/bin/env python

from bottle import Bottle, route, template, request

class Webservice(object):
    """docstring for Webservice"""
    def __init__(self, ip, port):
        
        self.app = Bottle()
        self.ip = ip
        self.port = port
        self.app.route('/', method='GET', callback=self.overview)


    def overview(self):
        return "hello world"


    def run(self):
        Bottle.run(self.app, host=self.ip, port=self.port)