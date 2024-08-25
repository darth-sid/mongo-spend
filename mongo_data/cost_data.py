from . import mongo_requests as mr
from . import cluster_data as cd

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

def get_cost_details(pub_key: str, priv_key: str,
                     start_date: str, end_date: str,
                     org_id: str, projects: list[str]=[], clusters: list[str]=[], services: list[str]=[],
                     group_by=GROUP_BY_ORG) -> dict:
    '''retrieves mongo atlas cost breakdowns, filtered by time period, org, projects, clusters, and services,
    grouped by spending per org, cluster, project, or service'''
    if not services:
        services=SERVICES
    if not projects:
        projects = cd.get_projects(pub_key=pub_key, priv_key=priv_key)
    if not clusters:
        clusters = [cluster[0] for cluster in cd.get_clusters(pub_key=pub_key, priv_key=priv_key, projects=projects)]
    payload = {"startDate": start_date,
               "endDate": end_date,
               "organizations": [org_id],
               "clusters": clusters,
               "projects": projects,
               "services": services,
               "groupBy": group_by}
    url = f"https://cloud.mongodb.com/api/atlas/v2/orgs/{org_id}/billing/costExplorer/usage" 
    cost_token_resp = mr.post(url=url, payload=payload, pub_key=pub_key, priv_key=priv_key)
    if cost_token_resp.status_code != 202:
        raise mr.RequestError(cost_token_resp) # TODO
    token = cost_token_resp.json()['token']
    cost_results_resp = mr.get(url=url+'/'+token, pub_key=pub_key, priv_key=priv_key)
    if cost_results_resp.status_code == 102:
        raise mr.RequestError(cost_token_resp) # TODO
    if cost_results_resp.status_code != 200:
        raise mr.RequestError(cost_token_resp) # TODO
    cost_results = {}
    cost_data = cost_results_resp.json()['usageDetails']
    if group_by == GROUP_BY_ORG:
        identifier = 'organizationId'
    elif group_by == GROUP_BY_CLUSTER:
        identifier = 'clusterId'
    elif group_by == GROUP_BY_PROJ:
        identifier = 'projectId'
    else:
        identifier = 'service'
    for cost_result in cost_data:
        c_id = cost_result[identifier]
        del cost_result[identifier]
        cost_results[c_id] = cost_result
    return cost_results
