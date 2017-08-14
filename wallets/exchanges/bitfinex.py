#!/usr/bin/env python

import requests
import json
import hashlib
import hmac
import time
import datetime

from .wallet import ExchangeWallet
from .translator import CurrencyTranslator


class Bitfinex(object):
    """Bitfinex API"""
    def __init__(self, apikey, apisecret):
        self.base_url = "https://api.bitfinex.com/"
        self.api_key = apikey
        self.api_secret = apisecret

    def _nonce(self):
        """
        Returns a nonce
        Used in authentication
        """
        return str(int(round(time.time() * 10000)))

    def _headers(self, path, nonce, body):
        signature = "/api/" + path + nonce + body
        h = hmac.new(self.api_secret.encode('utf-8'),
                     signature.encode('utf-8'), hashlib.sha384)
        signature = h.hexdigest()
        return {
            "bfx-nonce": nonce,
            "bfx-apikey": self.api_key,
            "bfx-signature": signature,
            "content-type": "application/json"
        }

    def req(self, path, params={}):
        nonce = self._nonce()
        body = params
        rawBody = json.dumps(body)
        headers = self._headers(path, nonce, rawBody)
        url = self.base_url + path
        resp = requests.post(url, headers=headers, data=rawBody, verify=True)
        resp.raise_for_status()
        return resp

    def wallets(self):
        """
        Fetch all active wallets
        """
        wallets = []
        response = self.req("v2/auth/r/wallets")
        timestamp = datetime.datetime.utcnow()
        #@todo fix error handling of api
        # sometimes the api responds with
        if 'error' in response.json():
            raise BaseException("unable to query bitfinex api. try again later")
        for wallet in response.json():
            wallets.append(ExchangeWallet(last_update=timestamp,
                                          wallet_type=wallet[0],
                                          currency=CurrencyTranslator.translate(wallet[1]), balance='{0:.8f}'.format(float(wallet[2]))))
        return wallets
