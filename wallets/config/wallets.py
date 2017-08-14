#!/usr/bin/env
"""

    configuration for the wallets app
"""

import os

class WalletsConfiguration(object):
    """ wallets configuration object """

    def __init__(self):
        """ initialize config """
        self.global_settings = {}
        self.global_settings['database'] = os.getenv('WALLETS_DATABASE','wallets.db')
        self.global_settings['schedule'] = os.getenv('WALLETS_SCHEDULE',None)

        # load exchanges
        self.exchanges = {}
        self._exchanges()


    def _exchanges(self):
        """ load exchanges if env variables are specified """

        # load kraken config
        if os.getenv('WALLETS_KRAKEN_KEY') and os.getenv('WALLETS_KRAKEN_SECRET'):
            self.exchanges.update({
                'Kraken' : {
                    'key': os.getenv('WALLETS_KRAKEN_KEY'),
                    'secret': os.getenv('WALLETS_KRAKEN_SECRET')
                }
            })
        # load bitfinex config
        if os.getenv('WALLETS_BITFINEX_KEY') and os.getenv('WALLETS_BITFINEX_SECRET'):
            self.exchanges.update({
                'Bitfinex' : {
                    'key': os.getenv('WALLETS_BITFINEX_KEY'),
                    'secret': os.getenv('WALLETS_BITFINEX_SECRET')
                }
            })