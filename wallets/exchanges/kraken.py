#!/usr/bin/env python

import krakenex
import datetime

from .wallet import ExchangeWallet
from .translator import CurrencyTranslator


class Kraken(object):
    """kraken API"""
    def __init__(self, apikey, apisecret):
        self.api_key = apikey
        self.api_secret = apisecret
        self.api = krakenex.API(key=self.api_key, secret=self.api_secret)

    def wallets(self):
        """
            get all active wallets from kraken
        """
        kraken_balance = self.api.query_private('Balance')
        if kraken_balance['error']:
            raise kraken_balance['error']

        wallets = []
        timestamp = datetime.datetime.utcnow()



        for currency, balance in kraken_balance['result'].items():
            wallets.append(ExchangeWallet(last_update=timestamp,
                                          currency=CurrencyTranslator.translate(currency),
                                          balance='{0:.8f}'.format(float(balance))))

        return wallets
