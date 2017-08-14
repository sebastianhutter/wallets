#!/usr/bin/env python

import requests

class CrytpoCompare(object):
    """docstring for CrytpoCompare"""
    def __init__(self, to_currency = ["BTC", "USD", "EUR"], exchange = 'CCCAGG'):
        self.base_url = "https://min-api.cryptocompare.com/data"
        self.to_currency = to_currency
        self.exchange = exchange


    def price(self, from_currency, to_currency=None, exchange=None):

        """
          query the current prices
        """

        if not to_currency:
          to_currency = self.to_currency

        if not exchange:
          exchange = self.exchange

        url = "{}/price".format(self.base_url)
        payload = {'fsym': from_currency,
                   'tsyms': str.join(',', to_currency),
                   'e': exchange}
        request = requests.get(url, params=payload)
        data = request.json()

        if 'Response' in data:
          if data['Response'] == 'Error':
            if 'market does not exist for this coin pair' in data['Message'] and exchange != self.exchange:
              return None
            else:
              raise BaseException("Unable to query rates for currency {}".format(currency))
        else:
          return data

    def price_historical(self, from_currency, timestamp,
                         to_currency=None, exchange=None):

        """
          query the historical prices
        """

        if not to_currency:
          to_currency = self.to_currency

        if not exchange:
          exchange = self.exchange


        url = "{}/pricehistorical".format(self.base_url)
        payload = {'fsym': from_currency,
                   'tsyms': str.join(',', to_currency),
                   'markets': exchange,
                   'ts': timestamp}
        request = requests.get(url, params=payload)

        print (request.json())