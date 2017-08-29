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
        # sqlite database gfile
        self.global_settings['database'] = os.getenv('WALLETS_DATABASE','wallets.db')
        # set to 0 to disable scheduled check of the wallets
        self.global_settings['schedule'] = os.getenv('WALLETS_SCHEDULE',0)
        # eecute a wallet scan at statup of the script, set to true / false
        self.global_settings['scanonstart'] = os.getenv('WALLETS_SCAN_ON_START',False)
        # set to true to enable webinterface for easier browsing
        self.global_settings['website'] = os.getenv('WALLETS_WEBSITE',False)
        # how much data should be displayed in the graphs on the overview page
        self.global_settings['overview_timeframe'] = os.getenv('WALLETS_OVERVIEW_TIME','5')
        self.global_settings['overview_modifier'] = os.getenv('WALLETS_OVERVIEW_MODIFIER','days')
        # tcp port the webservice is listening on 
        self.global_settings['port'] = os.getenv('WALLETS_WEBSITE_PORT',80)
        # ip addresss the webservice is listening on
        self.global_settings['ip'] = os.getenv('WALLETS_WEBSITE_IP','0.0.0.0')
        # verify valuess
        if str(self.global_settings['scanonstart']).lower() in ['true', '1', 't', 'y', 'yes' ]:
            self.global_settings['scanonstart'] = True
        else:
            self.global_settings['scanonstart'] = False
        if str(self.global_settings['website']).lower() in ['true', '1', 't', 'y', 'yes' ]:
            self.global_settings['website'] = True
        else:
            self.global_settings['website'] = False



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
        # load bittrex config
        if os.getenv('WALLETS_BITTREX_KEY') and os.getenv('WALLETS_BITTREX_SECRET'):
            self.exchanges.update({
                'Bittrex' : {
                    'key': os.getenv('WALLETS_BITTREX_KEY'),
                    'secret': os.getenv('WALLETS_BITTREX_SECRET')
                }
            })
        # load bitstamp config
        if os.getenv('WALLETS_BITSTAMP_KEY') and os.getenv('WALLETS_BITSTAMP_SECRET') and os.getenv('WALLETS_BITSTAMP_CUSTOMERID'):
            self.exchanges.update({
                'Bitstamp' : {
                    'key': os.getenv('WALLETS_BITSTAMP_KEY'),
                    'secret': os.getenv('WALLETS_BITSTAMP_SECRET'),
                    'customerid': os.getenv('WALLETS_BITSTAMP_CUSTOMERID')
                }
            })