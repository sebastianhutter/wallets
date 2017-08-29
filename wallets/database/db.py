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

    def get_exchanges(self):
        """
            returns a dict with all exchanges
        """
        cursor = self.connection.cursor()
        exchanges = []
        cursor.execute('SELECT id, name FROM exchange')
        result = cursor.fetchall()
        for r in result:
            exchanges.append({'id': r[0], 'name': r[1]})

        return exchanges

    def get_wallets_from_exchange(self, exchange_id):
        """
            retrieve all wallets for the specified exchange
        """
        cursor = self.connection.cursor()
        wallets = []
        cursor.execute('SELECT id, type, currency FROM wallet WHERE fk_exchange = ?',(exchange_id,))
        result = cursor.fetchall()
        for r in result:
            wallets.append({'id':r[0], 'type':r[1], 'currency':r[2]})

        return wallets

    def get_last_balance_from_wallet(self, wallet_id):
        """
            get the last balance from the specified wallet
        """
        cursor = self.connection.cursor()
        cursor.execute('SELECT timestamp, balance FROM balance WHERE fk_wallet = ? ORDER BY timestamp DESC LIMIT 1',(wallet_id,))
        result = cursor.fetchone()

        return {'timestamp':result[0], 'balance':result[1]}

    def get_last_rate_for_wallet_currency(self, wallet_id, timestamp, to_currency):
        """
            get the last conversion rates from the db
        """
        cursor = self.connection.cursor()
        data = ( wallet_id, wallet_id, timestamp, to_currency )
        cursor.execute('SELECT rate FROM rate WHERE fk_exchange = (SELECT fk_exchange FROM wallet WHERE id = ?) AND from_currency = (SELECT currency FROM WALLET WHERE id = ?) AND timestamp = ? AND to_currency = ?',data)
        result = cursor.fetchone()

        return (result[0])

    def get_balance_from_wallet(self, wallet_id, timeframe, modifier="days"):
        """
            get the last n days. hours, minutes of balances 
        """

        # lets make sure we use a supported time
        if not modifier in ["years", "months", "days", "hours", "minutes", "seconds"]:
            raise BaseException("unsupported modifier")


        cursor = self.connection.cursor()
        cursor.execute('SELECT timestamp, balance FROM balance WHERE fk_wallet = ? AND timestamp BETWEEN strftime(\'%s\',\'now\', \'-{} {}\', \'utc\') AND strftime(\'%s\',\'now\', \'utc\') ORDER BY timestamp'.format(int(timeframe),modifier),(wallet_id,))
        result = cursor.fetchall()

        balance = []
        for r in result:
            balance.append({'timestamp':r[0], 'balance':r[1]})

        return balance

    def get_rate_for_wallet(self, wallet_id, to_currency, timeframe, modifier="days"):
        """
            get the last conversion rates from the db
        """

        # lets make sure we use a supported time
        if not modifier in ["years", "months", "days", "hours", "minutes", "seconds"]:
            raise BaseException("unsupported modifier")

        cursor = self.connection.cursor()
        data = ( wallet_id, wallet_id, to_currency )
        cursor.execute('SELECT timestamp, rate FROM rate WHERE fk_exchange = (SELECT fk_exchange FROM wallet WHERE id = ?) AND from_currency = (SELECT currency FROM WALLET WHERE id = ?) AND to_currency = ? AND timestamp BETWEEN strftime(\'%s\',\'now\', \'-{} {}\', \'utc\') AND strftime(\'%s\',\'now\', \'utc\') ORDER BY timestamp'.format(int(timeframe),modifier),data)
        result = cursor.fetchall()

        rate = []
        for r in result:
            rate.append({'timestamp':r[0], 'rate':r[1]})


        return(rate)

    def get_balance_in_euro_from_wallet(self, wallet_id, timeframe, modifier="days"):
        # get the balance and the euro exchange rates from the db
        balance = self.get_balance_from_wallet(wallet_id, timeframe, modifier)
        rate = self.get_rate_for_wallet(wallet_id, 'EUR', timeframe, modifier)

        # merge balance and rate baed on timestamp
        # horribly inefficient but no motiviation to properly fix ;-)
        balance_with_rate = []      
        for b in balance:
            for r in rate:
                if b['timestamp'] == r['timestamp']:
                    balance_with_rate.append({'timestamp': b['timestamp'], 'rate': r['rate'], 'balance': b['balance'], 'euro': r['rate']*b['balance']})

        return balance_with_rate
