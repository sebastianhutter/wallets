#!/usr/bin/env python


class ExchangeWallet(object):
    """contains comman information for wallets retrieved form exchanges"""
    def __init__(self, currency, balance, last_update, wallet_type='exchange'):
        self.type = wallet_type
        self.currency = currency
        self.balance = balance
        self.last_update = last_update
