#!/usr/bin/env python

class CurrencyTranslator(object):
    """make sure all currencies are named the same in all different exchanges"""
    def __init__(self):
        pass

    @staticmethod
    def translate(currency):
        c = currency.upper()

        translations = {
            'ZEUR': "EUR",
            'XXBT': "BTC",
            "XBT" : "BTC",
            "XLTC": "LTC",
            'XETH': "ETH"
        }

        if c in translations:
            return translations[c]
        else:
            return c