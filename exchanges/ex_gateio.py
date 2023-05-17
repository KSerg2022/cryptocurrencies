import os
import requests
import time
import hashlib
import hmac

from dotenv import load_dotenv
load_dotenv()


class ExGate:
    """"""

    host = "https://api.gateio.ws"
    prefix = "/api/v4"
    headers = {'Accept': 'application/json', 'Content-Type': 'application/json'}
    query_param = ''

    def __init__(self):
        self.key = os.environ.get('GATE_API_KEY')  # api_key
        self.secret = os.environ.get('GATE_API_SECRET_KEY')  # api_secret

    def gen_sign(self, method, url, query_string=None, payload_string=None):
        """"""
        t = time.time()
        m = hashlib.sha512()
        m.update((payload_string or "").encode('utf-8'))
        hashed_payload = m.hexdigest()
        s = '%s\n%s\n%s\n%s\n%s' % (method, url, query_string or "", hashed_payload, t)
        sign = hmac.new(self.secret.encode('utf-8'), s.encode('utf-8'), hashlib.sha512).hexdigest()
        return {'KEY': self.key, 'Timestamp': str(t), 'SIGN': sign}

    def get_total_balance(self):
        """in USDT"""
        url = '/wallet/total_balance'
        return self._get_request(url)

    def get_account(self):
        """"""
        url = '/spot/accounts'
        currencies_account = self._get_request(url)
        currencies = self._normalize_data(currencies_account)
        return currencies

    def _get_request(self, url):
        """"""
        sign_headers = self.gen_sign('GET', self.prefix + url, self.query_param)
        self.headers.update(sign_headers)
        r = requests.request('GET', self.host + self.prefix + url, headers=self.headers)
        return r.json()

    @staticmethod
    def _normalize_data(currencies_account):
        """"""
        currencies = []
        for symbol in currencies_account:
            currencies.append({
                'coin': symbol['currency'].upper(),
                'bal': float(symbol['available']) + float(symbol['locked'])
            })
        return {os.path.splitext(os.path.basename(__file__))[0][3:]: sorted(currencies, key=lambda x: x['coin'])}


if __name__ == '__main__':
    currencies = ExGate()
    currencies.get_account()
