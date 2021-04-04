import hashlib
import hmac
import http.client
import json
import logging
import os
import sys
from time import time, strftime

class CoinSpot:
    endpoint = "www.coinspot.com.au"
    logging = "coinspot.log"

    def __init__(self, key, secret, host="www.coinspot.com.au", debug=False):
        self.timestamp = strftime("%d/%m/%Y %H:%M:%S")
        self.key = key
        self.secret = secret
        self.host = host
        self.debug = debug
        if self.debug:
            self.start_logging()

    def start_logging(self):
        logging.basicConfig(filename=os.path.realpath(os.path.dirname(sys.argv[0]))+"/"+self.logging, level=logging.DEBUG)

    def _get_signed_request(self, data):
        return hmac.new(self.secret.encode('utf-8'), data.encode('utf-8'), hashlib.sha512).hexdigest()

    def _request(self, path, postdata):
        nonce = int(time()*1000000)
        postdata['nonce'] = nonce
        params = json.dumps(postdata, separators=(',', ':'))
        signedMessage = self._get_signed_request(params)
        headers = {}
        headers['Content-type'] = 'application/json'
        headers['Accept'] = 'text/plain'
        headers['key'] = self.key
        headers['sign'] = signedMessage
        if self.debug:
            logging.warning(self.timestamp+" "+str(headers))
        conn = http.client.HTTPSConnection(self.endpoint)
        if self.debug:
            conn.set_debuglevel(1)
        response_data = '{"status":"invalid","error": "Did not make request"}'
        try:
            conn.request("POST", path, params, headers)
            response = conn.getresponse()
            if self.debug:
                logging.warning(self.timestamp+" "+str(response))
                logging.warning(self.timestamp+" "+str(response.msg))
            # print response.status, response.reason
            response_data = response.read().decode("utf-8")
            if self.debug:
                logging.warning(self.timestamp+" "+str(response_data))
            conn.close()
        except IOError as error:
            if self.debug:
                error_text = "Attempting to make request I/O error({0}): {1}".format(error.errno, error.strerror)
                logging.warning(self.timestamp+" "+error_text)
                response_data = '{"status":"invalid","error": "'+error_text+'"}'
        except:
            exit("Unexpected error: {0}".format(sys.exc_info()[0]))

        return json.loads(response_data)

    def sendcoin(self, cointype, address, amount):
        """
        Send coins
        :param cointype:
            the coin shortname in uppercase, example value 'BTC', 'LTC', 'DOGE'
        :param address:
            the address to send the coins to
        :param amount:
            the amount of coins to send
        :return:
            - **status** - ok, error
        """
        request_data = {'cointype': cointype, 'address': address, 'amount': amount}
        return self._request('/api/my/coin/send', request_data)

    def coindeposit(self, cointype):
        """
        Deposit coins
        :param cointype:
            the coin shortname in uppercase, example value 'BTC', 'LTC', 'DOGE'
        :return:
            - **status** - ok, error
            - **address** - your deposit address for the coin
        """
        request_data = {'cointype': cointype}
        return self._request('/api/my/coin/deposit', request_data)

    def quotebuy(self, cointype, amount):
        """
        Quick buy quote
        Fetches a quote on rate per coin and estimated timeframe to buy an amount of coins
        :param cointype:
            the coin shortname in uppercase, example value 'BTC', 'LTC', 'DOGE'
        :param amount:
            the amount of coins to sell
        :return:
            - **status** - ok, error
            - **quote** - the rate per coin
            - **timeframe** - estimate of hours to wait for trade to complete (0 = immediate trade)
        """
        request_data = {'cointype': cointype, 'amount': amount}
        return self._request('/api/quote/buy', request_data)

    def quotesell(self, cointype, amount):
        """
        Quick sell quote
        Fetches a quote on rate per coin and estimated timeframe to sell an amount of coins
        :param cointype:
            the coin shortname in uppercase, example value 'BTC', 'LTC', 'DOGE'
        :param amount:
            the amount of coins to sell
        :return:
            - **status** - ok, error
            - **quote** - the rate per coin
            - **timeframe** - estimate of hours to wait for trade to complete (0 = immediate trade)
        """
        request_data = {'cointype': cointype, 'amount': amount}
        return self._request('/api/quote/sell', request_data)

    def spot(self):
        """
        Fetch the latest spot prices
        :return:
            - **status** - ok, error
            - **spot**  - a list of the current spot price for each coin type
        """
        return self._request('/api/spot', {})

    def balances(self):
        """
        List my balances
        :return:
            - **status** - ok, error
            - **balances** - object containing one property for each coin with your balance for that coin.
        """
        return self._request('/api/my/balances', {})

    def orderhistory(self, cointype):
        """
        Lists the last 1000 completed orders
        :param cointype:
            the coin shortname in uppercase, example value 'BTC', 'LTC', 'DOGE'
        :return:
            - **status** - ok, error
            - **orders** - list of the last 1000 completed orders
        """
        request_data = {'cointype': cointype}
        return self._request('/api/orders/history', request_data)

    def orders(self, cointype):
        """
        Lists all open orders
        :param cointype:
            the coin shortname in uppercase, example value 'BTC', 'LTC', 'DOGE'
        :return:
            - **status** - ok, error
            - **buyorders** - array containing all the open buy orders
            - **sellorders** - array containing all the open sell orders
        """
        request_data = {'cointype': cointype}
        return self._request('/api/orders', request_data)

    def myorders(self):
        """
        List my buy and sell orders
        :return:
            - **status** - ok, error
            - **buyorders** - array containing all your buy orders
            - **sellorders** - array containing all your sell orders
        """
        return self._request('/api/my/orders', {})

    def buy(self, cointype, amount, rate):
        """
        Place buy orders
        :param cointype:
            the coin shortname in uppercase, example value 'BTC', 'LTC', 'DOGE'
        :param amount:
            the amount of coins you want to buy, max precision 8 decimal places
        :param rate:
            the rate in AUD you are willing to pay, max precision 6 decimal places
        :return:
            - **status** - ok, error
        """
        request_data = {'cointype': cointype, 'amount': amount, 'rate': rate}
        return self._request('/api/my/buy', request_data)

    def sell(self, cointype, amount, rate):
        """
        Place sell orders
        :param cointype:
            the coin shortname in uppercase, example value 'BTC', 'LTC', 'DOGE'
        :param amount:
            the amount of coins you want to sell, max precision 8 decimal places
        :param rate:
            the rate in AUD you are willing to sell for, max precision 6 decimal places
        :return:
            - **status** - ok, error
        """
        request_data = {'cointype': cointype, 'amount': amount, 'rate': rate}
        self._request('/api/my/sell', request_data)
