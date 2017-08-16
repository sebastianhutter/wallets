#!/usr/bin/env python

from bottle import Bottle, route, template, request
from database import db
import math
import time

class Webservice(object):
    """docstring for Webservice"""
    def __init__(self, ip, port, database):
        
        self.app = Bottle()
        self.ip = ip
        self.port = port
        self.app.route('/', method='GET', callback=self.overview)

        self.database = db.Database(database)

    def overview(self):
        #return "hello world"

        message = ""
        exchanges = self.database.get_exchanges()
        for e in exchanges:
            message = message + "Exchange - Name: {}<br/>".format(e['name'])
            wallets = self.database.get_wallets_from_exchange(e['id'])
            exchange_sum = 0
            for w in wallets:
                last_balance = self.database.get_last_balance_from_wallet(w['id'])
                exchange_rate_EUR =self.database.get_last_rate_for_wallet_currency(wallet_id=w['id'], timestamp=last_balance['timestamp'], to_currency="EUR")
                balance_in_EUR = math.ceil(last_balance['balance']*exchange_rate_EUR)
                date = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(last_balance['timestamp']))
                exchange_sum = exchange_sum + balance_in_EUR
                message = message +  "Wallet - Currency: {}, Type: {}, Timestamp: {}, Exchange Rate EUR: {}, Balance: {}, Balance in EUR: {}<br/>".format(w['currency'],w['type'],date,exchange_rate_EUR,last_balance['balance'],balance_in_EUR)

                #p1.line(datetime("2017-05-05 10:10:10"), last_balance, legend=w['currency'])
            message = message + "Amount of EURO in Exchange {}: {} <br/><br/>".format(e['name'],exchange_sum)

        return message

    def run(self):
        Bottle.run(self.app, host=self.ip, port=self.port)