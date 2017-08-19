#!/usr/bin/env python

import requests
import json
import hashlib
import hmac
import time
import datetime

from .wallet import ExchangeWallet
from .translator import CurrencyTranslator


class Bittrex(object):
    """Bittrex API"""
    def __init__(self, apikey, apisecret):
        self.base_url = "https://bittrex.com/api/"
        self.api_key = apikey
        self.api_secret = apisecret

    def _nonce(self):
        """
        Returns a nonce
        Used in authentication
        """
        return str(int(round(time.time() * 10000)))

    def _headers(self, url, params):
        # create url from url and params
        # 2017-08-19 https://stackoverflow.com/questions/18869074/create-url-without-request-execution
        url = requests.Request('GET', url, params=params).prepare().url
        print(url)
        h = hmac.new(self.api_secret.encode(), url.encode(), hashlib.sha512)
        signature = h.hexdigest()

        return {
            "apisign": signature,
            "content-type": "application/json"
        }

    def req(self, path, params={}):
        nonce = self._nonce()
        #headers = self._headers(path, nonce, rawBody)
        params['apikey'] = self.api_key
        params['nonce'] = self._nonce()
        url = self.base_url + path
        headers = self._headers(url, params)

        print (headers)

        resp = requests.get(url, headers=headers, params=params, verify=True)
        resp.raise_for_status()
        return resp

    def wallets(self):
        """
        Fetch all active wallets
        """
        wallets = []
        response = self.req(path="v1.1/account/getbalances")
        timestamp = datetime.datetime.utcnow()

        #@todo fix error handling of api
        if not response.json()['success']:
            raise BaseException("unable to query bittrex api. try again later")

        for wallet in response.json()['result']:
            wallets.append(ExchangeWallet(last_update=timestamp,
                                          currency=CurrencyTranslator.translate(wallet['Currency']),
                                          balance='{0:.8f}'.format(float(wallet['Balance']))))
        return wallets

