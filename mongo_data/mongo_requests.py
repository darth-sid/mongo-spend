import requests
from requests.auth import HTTPDigestAuth

class RequestError(Exception):
    def __init__(self, resp: requests.Response):
        self.code = resp.status_code
        self.msg = resp.reason

def get(url, pub_key, priv_key) -> requests.Response:
    '''makes a digest auth conforming http get request'''

    auth = HTTPDigestAuth(pub_key,priv_key)
    headers = {
        'Content' : 'application/json',
        'Accept': 'application/vnd.atlas.2024-05-30+json'
    }
    return requests.get(url, headers=headers, auth=auth)

def post(url, payload, pub_key, priv_key) -> requests.Response:
    '''makes a digest auth conforming http post request'''

    auth = HTTPDigestAuth(pub_key, priv_key)
    headers = {
        'Content' : 'application/json',
        'Accept': 'application/vnd.atlas.2024-05-30+json'
    }
    return requests.post(url, headers=headers, auth=auth, json=payload)
