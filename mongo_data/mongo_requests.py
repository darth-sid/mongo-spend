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
        'Content-Type' : 'application/json',
        'Accept': 'application/vnd.atlas.2024-08-05+json'
    }
    return requests.get(url, headers=headers, auth=auth)

def post(url, payload, pub_key, priv_key) -> requests.Response:
    '''makes a digest auth conforming http post request'''

    auth = HTTPDigestAuth(pub_key, priv_key)
    headers = {
        'Content-Type' : 'application/json',
        'Accept': 'application/vnd.atlas.2024-08-05+json'
    }
    return requests.post(url, headers=headers, auth=auth, json=payload)

def patch(url, data, pub_key, priv_key) -> requests.Response:
    '''makes a digest auth conforming http patch request'''

    auth = HTTPDigestAuth(pub_key, priv_key)
    headers = {
        'Content-Type' : 'application/json',
        'Accept': 'application/vnd.atlas.2024-08-05+json'
    }
    print(data)
    return requests.patch(url, headers=headers, auth=auth, data=data)
