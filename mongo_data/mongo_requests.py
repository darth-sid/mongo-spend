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

def patch(url, data, pub_key, priv_key) -> requests.Response:
    '''makes a digest auth conforming http patch request'''

    auth = HTTPDigestAuth(pub_key, priv_key)
    headers = {
        'Content' : 'application/json',
        'Accept': 'application/vnd.atlas.2024-05-30+json'
    }
    print(data)
    return requests.patch(url, headers=headers, auth=auth, data=data)

import json
url = 'https://cloud.mongodb.com/api/atlas/v2/groups/667d928c88550259e571f718/clusters/Cluster1'
#print(data2:=get(url,'ybjcmsrb','0822f1cd-6bbe-4c9b-a742-22ec1bb2b7ae').json())
data = {'paused':False}
print(patch(url,{},'ybjcmsrb','0822f1cd-6bbe-4c9b-a742-22ec1bb2b7ae').reason)
