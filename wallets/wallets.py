#!/usr/bin/env python

#
# no config in place yet. lets hardcode some stuff
#


#
# filling in the db is now possible. next step is to get the values from the db
# - current amount of money per wallet, per exchange and total
# - plotting of wallets per exchange and their trade value
#


import traceback
import logging

from threading import Timer

from exchanges.bitfinex import Bitfinex
from exchanges.kraken import Kraken
from exchanges.bittrex import Bittrex
from exchanges.bitstamp import Bitstamp
from cryptocompare import cryptocompare
from database import db

from config.wallets import WalletsConfiguration

from webservice.service import Webservice

import bottle

# configure logger
# http://docs.python-guide.org/en/latest/writing/logging/
logger = logging.getLogger()
handler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s %(name)-12s %(levelname)-8s %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)
# by default set logger to info. can be overwritten by checkhttpconfig.loglevel
logger.setLevel(logging.INFO)


#
# functions
#

def query_exchanges(exchanges, database_file, schedule=None):
    """
        query the given exchanges for the wallets and exchange rates
        write values into given database object
    """

    # loop trough the exchanges
    # query all wallets
    # write wallets and current values into database
    database = db.Database(database_file)
    rates = cryptocompare.CrytpoCompare()
    try:
        for exchange in exchanges:
            try:
                # set the exchange name
                exchange_name = exchange.__class__.__name__
                # lets get the wallets from the exchange
                wallets = exchange.wallets()
                # lets loop over the wallets and write them into the database
                for wallet in wallets:
                    # make sure all the wallets exist in the database
                    database.update_wallet(exchange_name=exchange_name, wallet_type=wallet.type, wallet_currency=wallet.currency)
                    # now write the current balance and timestamp to the db
                    database.insert_balance(exchange_name=exchange_name, wallet_type=wallet.type, wallet_currency=wallet.currency, wallet_balance=wallet.balance, wallet_timestamp=wallet.last_update.strftime('%s'))

                    # lets get an approximation of the value of the currenct
                    # historical price is not necessary up to date when running the request so we run against the current price
                    exchange_rates = rates.price(from_currency=wallet.currency, exchange=exchange_name)
                    if not exchange_rates:
                        exchange_rates = rates.price(from_currency=wallet.currency)
                    # now add the rates to the database
                    for from_currency, currency_rates in exchange_rates.items():
                        for to_currency, rate in currency_rates.items():
                            database.insert_rates(exchange_name=exchange_name, from_currency=from_currency, to_currency=to_currency, rate=rate, rate_timestamp=wallet.last_update.strftime('%s'))

            except BaseException as err:
                logger.error("problem encountered while requesting wallets from {}. error message: {}".format(exchange_name, err))

    except Exception as err:
        raise

    if schedule: 
        Timer(int(schedule), query_exchanges, args=(exchanges,database_file,schedule)).start()

#
# main
#

    
if __name__ == '__main__':
    try:
        configuration = WalletsConfiguration()
        # initialuze the different exchanges
        database = db.Database(configuration.global_settings['database'])
        exchanges = []
        for name,value in configuration.exchanges.items():
            # create the exchange object
            if name == "Bitstamp":
                exchange = eval(name)(value['customerid'], value['key'],value['secret'])
            else:
                exchange = eval(name)(value['key'],value['secret'])
            exchanges.append(exchange)
            # and make sure the exchange is registered in the database
            database.update_exchange(name)
        database = None

        # now lets start reading our current wallets from the different exchanges
        if int(configuration.global_settings['schedule']) > 0:
            query_exchanges(exchanges, configuration.global_settings['database'], configuration.global_settings['schedule'])
        if configuration.global_settings['scanonstart']:
            query_exchanges(exchanges, configuration.global_settings['database'])

        if configuration.global_settings['website']:
            # create configuration for the webserivce
            service_config = {
                'ip': configuration.global_settings['ip'],
                'port': configuration.global_settings['port'],
                'database': configuration.global_settings['database'],
                'server': configuration.global_settings['server'],
                'overview': {
                    'timeframe': configuration.global_settings['overview_timeframe'],
                    'modifier': configuration.global_settings['overview_modifier'],
                }
            }
            # start bottle webapp
            service = Webservice(configuration=service_config)
            service.run()

    except Exception as err:
        logger.error(err)
        traceback.print_exc()

    


