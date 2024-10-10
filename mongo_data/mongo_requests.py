import requests
from requests.auth import HTTPDigestAuth
import json

class RequestError(Exception):
    def __init__(self, resp: requests.Response):
        self.code = resp.status_code
        self.msg = resp.reason

def get(url: str, pub_key: str, priv_key: str) -> requests.Response:
    '''makes a digest auth conforming http get request'''

    auth = HTTPDigestAuth(pub_key,priv_key)
    headers = {
        'Content-Type' : 'application/json',
        'Accept': 'application/vnd.atlas.2024-08-05+json'
    }
    return requests.get(url, headers=headers, auth=auth)

def post(url: str, payload: dict, pub_key: str, priv_key: str) -> requests.Response:
    '''makes a digest auth conforming http post request'''

    auth = HTTPDigestAuth(pub_key, priv_key)
    headers = {
        'Content-Type' : 'application/json',
        'Accept': 'application/vnd.atlas.2024-08-05+json'
    }
    return requests.post(url, headers=headers, auth=auth, json=json.dumps(payload))

def patch(url: str, data: dict, pub_key: str, priv_key: str) -> requests.Response:
    '''makes a digest auth conforming http patch request'''

    auth = HTTPDigestAuth(pub_key, priv_key)
    headers = {
        'Content-Type' : 'application/json',
        'Accept': 'application/vnd.atlas.2024-08-05+json'
    }
    print(data)
    return requests.patch(url, headers=headers, auth=auth, data=json.dumps(data))
