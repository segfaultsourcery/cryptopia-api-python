""" This is a wrapper for Cryptopia.co.nz API """

import base64
import hashlib
import hmac
import json
import time
import urllib
from pprint import pformat

import requests


class CryptopiaAPIException(Exception):
    def __init__(self, function_name, error, *args):
        super().__init__(*args)
        self.function_name = function_name
        self.error = error

    def __str__(self):
        type_name = type(self).__name__
        return f"{type_name}(function_name={self.function_name!r}): {pformat(self.error)}"

    __repr__ = __str__


def unwrap(fn):
    """
    Unwraps query results in the format {"Success": True, "Data": blah, "Message": blah}.
    """

    def _wrapper(*args, **kw):
        response = fn(*args, **kw).json()

        if not response['Success']:
            raise CryptopiaAPIException(fn.__name__, response['Error'])

        if 'Message' in response and response['Message']:
            print("# The API sent the following message:", response['Message'])

        return response['Data']

    _wrapper.__name__ = fn.__name__
    _wrapper.__doc__ = fn.__doc__

    return _wrapper


class Api(object):
    """ Represents a wrapper for cryptopia API """

    def __init__(self, key, secret):
        self.key = key
        self.secret = secret
        self.public = (
            'GetCurrencies',
            'GetTradePairs',
            'GetMarkets',
            'GetMarket',
            'GetMarketHistory',
            'GetMarketOrders',
            'GetMarketOrderGroups')

        self.private = (
            'GetBalance',
            'GetDepositAddress',
            'GetOpenOrders',
            'GetTradeHistory',
            'GetTransactions',
            'SubmitTrade',
            'CancelTrade',
            'SubmitTip',
            'SubmitWithdraw',
            'SubmitTransfer')

    @unwrap
    def api_query(self, feature_requested, get_parameters=None, post_parameters=None):
        """ Performs a generic api request """

        if feature_requested in self.private:
            url = f"https://www.cryptopia.co.nz/Api/{feature_requested}"
            post_data = json.dumps(post_parameters)
            headers = self.secure_headers(url=url, post_data=post_data)
            return requests.post(url, data=post_data, headers=headers)

        if feature_requested in self.public:
            get_parameters = ('/'.join(i for i in get_parameters.values()) if get_parameters is not None else "")
            url = f"https://www.cryptopia.co.nz/Api/{feature_requested}/{get_parameters}"
            return requests.get(url, params=get_parameters)

        raise Exception(f"Unknown feature: {feature_requested}.")

    def get_currencies(self):
        """ Gets all the currencies """
        return self.api_query(
            feature_requested='GetCurrencies')

    def get_tradepairs(self):
        """ Gets all the trade pairs """
        return self.api_query(
            feature_requested='GetTradePairs')

    def get_markets(self):
        """ Gets data for all markets """
        return self.api_query(
            feature_requested='GetMarkets')

    def get_market(self, market):
        """ Gets market data """
        return self.api_query(
            feature_requested='GetMarket',
            get_parameters={'market': market})

    def get_history(self, market):
        """ Gets the full order history for the market (all users) """
        return self.api_query(
            feature_requested='GetMarketHistory',
            get_parameters={'market': market})

    def get_orders(self, market):
        """ Gets the user history for the specified market """
        return self.api_query(
            feature_requested='GetMarketOrders',
            get_parameters={'market': market})

    def get_ordergroups(self, markets):
        """ Gets the order groups for the specified market """
        return self.api_query(
            feature_requested='GetMarketOrderGroups',
            get_parameters={'markets': markets})

    def get_balance(self, currency):
        """ Gets the balance of the user in the specified currency """
        return self.api_query(
            feature_requested='GetBalance',
            post_parameters={'Currency': currency})

    def get_openorders(self, market):
        """ Gets the open order for the user in the specified market """
        return self.api_query(
            feature_requested='GetOpenOrders',
            post_parameters={'Market': market})

    def get_deposit_address(self, currency):
        """ Gets the deposit address for the specified currency """
        return self.api_query(
            feature_requested='GetDepositAddress',
            post_parameters={'Currency': currency})

    def get_tradehistory(self, market):
        """ Gets the trade history for a market """
        return self.api_query(
            feature_requested='GetTradeHistory',
            post_parameters={'Market': market})

    def get_transactions(self, transaction_type):
        """ Gets all transactions for a user """
        return self.api_query(
            feature_requested='GetTransactions',
            post_parameters={'Type': transaction_type})

    def submit_trade(self, market, trade_type, rate, amount):
        """ Submits a trade """
        return self.api_query(
            feature_requested='SubmitTrade',
            post_parameters={
                'Market': market,
                'Type': trade_type,
                'Rate': rate,
                'Amount': amount})

    def cancel_trade(self, trade_type, order_id, tradepair_id):
        """ Cancels an active trade """
        return self.api_query(
            feature_requested='CancelTrade',
            post_parameters={
                'Type': trade_type,
                'OrderID': order_id,
                'TradePairID': tradepair_id})

    def submit_tip(self, currency, active_users, amount):
        """ Submits a tip """
        return self.api_query(
            feature_requested='SubmitTip',
            post_parameters={
                'Currency': currency,
                'ActiveUsers': active_users,
                'Amount': amount})

    def submit_withdraw(self, currency, address, amount):
        """ Submits a withdraw request """
        return self.api_query(
            feature_requested='SubmitWithdraw',
            post_parameters={
                'Currency': currency,
                'Address': address,
                'Amount': amount})

    def submit_transfer(self, currency, username, amount):
        """ Submits a transfer """
        return self.api_query(
            feature_requested='SubmitTransfer',
            post_parameters={
                'Currency': currency,
                'Username': username,
                'Amount': amount})

    def secure_headers(self, url, post_data):
        """ Creates secure header for cryptopia private api. """
        key = self.key
        secret = self.secret
        nonce = str(int(time.time() * 100000))

        md5 = hashlib.md5()
        md5.update(post_data.encode('utf-8'))

        hashed_post_params = base64.b64encode(md5.digest()).decode('utf-8')

        signature = ''.join((
            key,
            "POST",
            urllib.parse.quote_plus(url).lower(),
            nonce,
            hashed_post_params)
        ).encode('utf-8')

        hmacsignature = (
            base64.b64encode(
                hmac.new(
                    base64.b64decode(secret),
                    signature,
                    hashlib.sha256)
                    .digest())
                .decode('utf-8'))

        return {
            'Authorization': f'amx {key}:{hmacsignature}:{nonce}',
            'Content-Type': 'application/json; charset=utf-8'
        }
