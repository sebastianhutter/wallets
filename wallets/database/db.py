    #!/usr/bin/env python3

import sqlite3

class Database(object):
    """docstring for Database"""
    def __init__(self, database):
        self.file = database

        try:
            self.connection = sqlite3.connect(self.file)
            self._setup()
        except Exception as e:
            raise

    def _setup(self):
        """
            creates necessary tables
        """
        cursor = self.connection.cursor()

        cursor.execute('CREATE TABLE IF NOT EXISTS exchange (id integer PRIMARY KEY, name text NOT NULL)')
        cursor.execute('CREATE TABLE IF NOT EXISTS wallet (id integer PRIMARY KEY, fk_exchange integer NOT NULL, type text NOT NULL, currency test NOT NULL, FOREIGN KEY (fk_exchange) REFERENCES exchange(id))')
        cursor.execute('CREATE TABLE IF NOT EXISTS balance (fk_wallet integer NOT NULL, timestamp integer NOT NULL, balance float NOT NULL, FOREIGN KEY (fk_wallet) REFERENCES wallet(id))')
        cursor.execute('CREATE TABLE IF NOT EXISTS rate (fk_exchange integer NOT NULL, timestamp integer NOT NULL, from_currency text NOT NULL, to_currency text NOT NULL, rate float NOT NULL, FOREIGN KEY (fk_exchange) REFERENCES exchange(id))')

        self.connection.commit()

    def update_exchange(self, exchange_name):
        """
            insert or update exchange in exchange table
        """
        # 2017-8-14: https://stackoverflow.com/questions/3634984/insert-if-not-exists-else-update
        cursor = self.connection.cursor()
        data = ( exchange_name, exchange_name, )
        cursor.execute('INSERT OR REPLACE INTO exchange (id, name) VALUES ((SELECT id from exchange WHERE name = ?), ?)', data)
        self.connection.commit()

    def update_wallet(self, exchange_name, wallet_type, wallet_currency):
        """
            insert or update wallets in the wallet table
        """
        cursor = self.connection.cursor()
        data = (exchange_name,)
        cursor.execute('SELECT id FROM exchange WHERE name = ?',data)
        exchange_id = cursor.fetchone()[0]

        data = ( exchange_id, wallet_type, wallet_currency, exchange_id, wallet_type, wallet_currency )
        cursor.execute('INSERT OR REPLACE INTO wallet (id, fk_exchange, type, currency) VALUES ((SELECT id from wallet WHERE fk_exchange = ? AND type = ? AND currency = ?), ?, ?, ?)', data)
        self.connection.commit()

    def insert_balance(self, exchange_name, wallet_type, wallet_currency, wallet_balance, wallet_timestamp):
        """
            insert the current balance with timestamp for the given wallet
        """

        cursor = self.connection.cursor()
        # get the exchange id
        data = (exchange_name,)
        cursor.execute('SELECT id FROM exchange WHERE name = ?',data)
        exchange_id = cursor.fetchone()[0]
        # get wallet id
        data = (exchange_id, wallet_type, wallet_currency)
        cursor.execute('SELECT id FROM wallet WHERE fk_exchange = ? AND type = ? AND currency = ?',data)
        wallet_id = cursor.fetchone()[0]
        data = (wallet_id, wallet_timestamp, format(float(wallet_balance), '.8f'),)
        cursor.execute('INSERT INTO balance VALUES (?, ?, ?)',data)
        self.connection.commit()

    def insert_rates(self, exchange_name, from_currency, to_currency, rate, rate_timestamp):
        """
            insert the current rate with timestamp for the given exchange
        """

        cursor = self.connection.cursor()
        # get the exchange id
        data = (exchange_name,)
        cursor.execute('SELECT id FROM exchange WHERE name = ?',data)
        exchange_id = cursor.fetchone()[0]
        # insert rate
        data = (exchange_id, rate_timestamp, from_currency, to_currency, rate)
        cursor.execute('INSERT INTO rate VALUES (?, ?, ?, ?, ?)',data)
        self.connection.commit()


