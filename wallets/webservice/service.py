#!/usr/bin/env python

from bottle import Bottle, route, run, template, request

import math
import time
import os
import numpy as np
from datetime import datetime

from bokeh.plotting import figure
from bkcharts import TimeSeries
from bokeh.embed import components
from bokeh.palettes import Category20
import pandas

from database import db


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

        # lets get the exchanges from the database
        exchanges = []
        exchanges_raw = self.database.get_exchanges()
        for e in exchanges_raw:
            exchange = { 'name': e['name'], 'wallets': [], 
                         'coin_graph': self._render_coin_balance_graph_exchange(5,e['id']), 
                         'rate_graph': self._render_rate_balance_graph_exchange(5,e['id']),
                         'total': 0
                        }
            wallets_raw = self.database.get_wallets_from_exchange(e['id'])
            for w in wallets_raw:
                balance = self.database.get_last_balance_from_wallet(w['id'])
                exchange_rate_EUR =self.database.get_last_rate_for_wallet_currency(wallet_id=w['id'], timestamp=balance['timestamp'], to_currency="EUR")
                balance_in_EUR = math.ceil(balance['balance']*exchange_rate_EUR)
                timestamp = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(balance['timestamp']))
                exchange['wallets'].append({'timestamp':timestamp, 'type': w['type'], 'currency': w['currency'], 'balance': balance['balance'], 'balance_euro': balance_in_EUR})
                exchange['total'] = exchange['total'] + balance_in_EUR
            exchanges.append(exchange)

        return template('overview', data={'exchanges': exchanges})


    def _render_coin_balance_graph_exchange(self, days, exchange_id):
        """ render timeline graph for specified date range and exchange """

        # prepare the plot
        p = figure(width=800, height=350, x_axis_type="datetime")
        p.title.text = "Coin Overview"
        p.legend.location = "top_left"
        p.grid.grid_line_alpha=0
        p.xaxis.axis_label = 'Date'
        p.yaxis.axis_label = 'Coin'
        p.ygrid.band_fill_color="olive"
        p.ygrid.band_fill_alpha = 0.1

        # get all wallets from the exchange
        wallets = self.database.get_wallets_from_exchange(exchange_id)

        # loop trough all wallets and prepare the balance
        loop_count = 0
        for w in wallets:
            # if we are working on EUROS we wont add it 
            if w['currency'] == "EUR":
                continue

            # get the last n days of balance data
            balance = self.database.get_balance_from_wallet(w['id'],days)
            # fix the dateformat for the balance entries
            for b in balance:
                time = datetime.fromtimestamp(b['timestamp'])
                b['timestamp']= datetime.strftime(time,"%Y-%m-%d %H:%M:%S.%f")

            # convert to matrix
            balance = pandas.DataFrame(balance)

            # from here we convert to numpy else somehow no graph is displayed
            np_balance_balance = np.array(balance['balance'])
            np_balance_timestamp = np.array(balance['timestamp'], dtype=np.datetime64)

            # add a line with the coins
            # was not able to get the timeline working so we randomize
            # our colors a little bit (will fail with more then 15 wallets in one exchange)
            p.line(np_balance_timestamp, np_balance_balance, color=Category20[15][loop_count], legend=w['currency'])
            loop_count = loop_count + 1
        script, div = components(p)

        return {'script': script, 'div': div}

    def _render_rate_balance_graph_exchange(self, days, exchange_id):
        """ render timeline graph for specified date range and exchange """

        # prepare the plot
        p = figure(width=800, height=150, x_axis_type="datetime")
        p.title.text = "Exchange Rate Overview"
        p.legend.location = "top_left"
        p.grid.grid_line_alpha=0
        p.xaxis.axis_label = 'Date'
        p.yaxis.axis_label = 'Exchange Rate'
        p.ygrid.band_fill_color="olive"
        p.ygrid.band_fill_alpha = 0.1

        # get all wallets from the exchange
        wallets = self.database.get_wallets_from_exchange(exchange_id)

        # loop trough all wallets and prepare the balance
        loop_count = 0
        for w in wallets: 
            # if we are working on EUROS we wont add it 
            if w['currency'] == "EUR":
                continue
            # get the last n days of exachange rates
            rate = self.database.get_rate_for_wallet(w['id'],'EUR',days)
            # fix the dateformat for the balance entries
            for r in rate:
                time = datetime.fromtimestamp(r['timestamp'])
                r['timestamp']= datetime.strftime(time,"%Y-%m-%d %H:%M:%S.%f")

            # create a panda matrix
            rate = pandas.DataFrame(rate)
            # from here we convert to numpy else somehow no graph is displayed
            np_rate_rate= np.array(rate['rate'])
            np_rate_timestamp = np.array(rate['timestamp'], dtype=np.datetime64)
   
            p.circle(np_rate_timestamp, np_rate_rate, color=Category20[15][loop_count], legend="exchange rate {}".format(w['currency']))

            loop_count = loop_count + 1

        script, div = components(p)

        return {'script': script, 'div': div}

    def run(self):
        Bottle.run(self.app, host=self.ip, port=self.port)