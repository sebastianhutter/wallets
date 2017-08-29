#!/usr/bin/env python

import requests
import json
import hashlib
import hmac
import time
import datetime

from .wallet import ExchangeWallet
from .translator import CurrencyTranslator


class Bitstamp(object):
    """Bittrex API"""
    def __init__(self, customerid, apikey, apisecret):
        self.base_url = "https://www.bitstamp.net/api/"
        self.customerid = customerid
        self.api_key = apikey
        self.api_secret = apisecret

    def _nonce(self):
        """
        Returns a nonce
        Used in authentication
        """
        return str(int(round(time.time() * 10000)))

    def _headers(self):
        # create url from url and params
        # 2017-08-19 https://stackoverflow.com/questions/18869074/create-url-without-request-execution

        #nonce = self._nonce()
        #message = '{}{}{}'.format(nonce, self.customerid, self.api_key)

        #h = hmac.new(self.api_secret.encode(),  msg=message.encode, digestmod=hashlib.sha256)
        #signature = h.hexdigest().upper()

        return {
            #"signature": signature,
            #"nonce": nonce,
            "content-type": "application/json"
        }

    def req(self, path, params={}):


        nonce = self._nonce()
        message = '{}{}{}'.format(nonce, self.customerid, self.api_key)

        h = hmac.new(self.api_secret.encode(),  msg=message.encode(), digestmod=hashlib.sha256)
        signature = h.hexdigest().upper()


        url = self.base_url + path

        resp = requests.post(url, data={
            'key': self.api_key,
            'nonce': nonce,
            'signature': signature,
        })

        resp.raise_for_status()
        return resp

    def wallets(self):
        """
        Fetch all active wallets
        """
        wallets = []
        response = self.req(path="v2/balance/")
        timestamp = datetime.datetime.utcnow()


        for wallet,value in response.json().items():
            if "_balance" in wallet:
                currency = wallet.replace("_balance","")
                balance = value

                wallets.append(ExchangeWallet(last_update=timestamp,
                                          currency=CurrencyTranslator.translate(currency),
                                          balance='{0:.8f}'.format(float(balance))))


        return wallets

