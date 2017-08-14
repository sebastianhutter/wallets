#!/usr/bin/env python

class CurrencyTranslator(object):
    """make sure all currencies are named the same in all different exchanges"""
    def __init__(self):
        pass

    @staticmethod
    def translate(currency):
        translations = {
            'ZEUR': "EUR",
            'XXBT': "BTC",
            "XBT" : "BTC",
            "XLTC": "LTC",
            'XETH': "ETH"
        }

        if currency in translations:
            return translations[currency]
        else:
            return currency