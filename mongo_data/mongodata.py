import requests
from requests.auth import HTTPDigestAuth

class RequestError(Exception):
    def __init__(self, resp: requests.Response):
        self.code = resp.status_code
        self.msg = resp.reason

GROUP_BY_ORG = "organizations"
GROUP_BY_CLUSTER = "clusters"
GROUP_BY_PROJ = "projects"
GROUP_BY_SERVICE = "services"

SERVICES = ["Atlas",
            "Clusters",
            "Storage",
            "Serverless Instances",
            "Backup",
            "Data Transfer",
            "BI Connector",
            "Premium Features",
            "Atlas Data Federation",
            "Atlas Stream Processing",
            "App Services",
            "Charts",]

def _get(url, pub_key, priv_key):
    '''makes a digest auth conforming http get request'''

    auth = HTTPDigestAuth(pub_key,priv_key)
    headers = {
        'Content' : 'application/json',
        'Accept': 'application/vnd.atlas.2024-05-30+json'
    }
    return requests.get(url, headers=headers, auth=auth)

def _post(url, payload, pub_key, priv_key):
    '''makes a digest auth conforming http post request'''

    auth = HTTPDigestAuth(pub_key, priv_key)
    headers = {
        'Content' : 'application/json',
        'Accept': 'application/vnd.atlas.2024-05-30+json'
    }
    return requests.post(url, headers=headers, auth=auth, json=payload)

def get_cost_details(pub_key: str, priv_key: str,
                     start_date: str, end_date: str,
                     org_id: str, projects: list[str]=[], clusters: list[str]=[], services: list[str]=[],
                     group_by=GROUP_BY_ORG) -> dict:
    '''retrieves mongo atlas cost breakdowns, filtered by time period, org, projects, clusters, and services,
    grouped by spending per org, cluster, project, or service'''
    if not services:
        services=SERVICES
    if not projects:
        projects_resp=_get("https://cloud.mongodb.com/api/atlas/v2/groups", pub_key=pub_key, priv_key=priv_key)
        if projects_resp.status_code != 200:
            raise RequestError(projects_resp) # TODO
        projects = [result['id'] for result in projects_resp.json()['results']]
    if not clusters:
        clusters = []
        for project in projects:
            clusters_resp = _get(f"https://cloud.mongodb.com/api/atlas/v2/groups/{project}/clusters", pub_key=pub_key, priv_key=priv_key)
            if clusters_resp.status_code != 200:
                raise RequestError(clusters_resp) # TODO
            c = [result['id'] for result in clusters_resp.json()['results']]
            clusters.extend(c)
    payload = {"startDate": start_date,
               "endDate": end_date,
               "organizations": [org_id],
               "clusters": clusters,
               "projects": projects,
               "services": services,
               "groupBy": group_by}
    url = f"https://cloud.mongodb.com/api/atlas/v2/orgs/{org_id}/billing/costExplorer/usage" 
    print(url,payload)
    cost_token_resp = _post(url=url, payload=payload, pub_key=pub_key, priv_key=priv_key)
    if cost_token_resp.status_code != 202:
        raise RequestError(cost_token_resp) # TODO
    token = cost_token_resp.json()['token']
    print(token)
    cost_results_resp = _get(url=url+'/'+token, pub_key=pub_key, priv_key=priv_key)
    if cost_results_resp.status_code == 102:
        raise RequestError(cost_token_resp) # TODO
    print("almost")
    if cost_results_resp.status_code != 200:
        raise RequestError(cost_token_resp) # TODO
    return cost_results_resp.json()
