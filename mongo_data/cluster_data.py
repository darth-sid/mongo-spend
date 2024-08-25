from . import mongo_requests as mr
from datetime import datetime

def get_projects(pub_key: str, priv_key: str) -> list[str]:
    '''retrieves all projects visible to the given api key pair'''
    projects_resp = mr.get("https://cloud.mongodb.com/api/atlas/v2/groups", pub_key=pub_key, priv_key=priv_key)
    if projects_resp.status_code != 200:
        raise mr.RequestError(projects_resp) # TODO
    return [result['id'] for result in projects_resp.json()['results']]


def get_clusters(pub_key: str, priv_key: str, projects: list[str]=[], keys: list[str]=['id']) -> list[tuple]:
    '''retrieves requested cluster data for given projects or all clusters visible to the given api key pair'''
    if not projects:
        projects = get_projects(pub_key=pub_key, priv_key=priv_key)
    clusters = [] 
    for project in projects:
        clusters_resp = mr.get(f"https://cloud.mongodb.com/api/atlas/v2/groups/{project}/clusters", pub_key=pub_key, priv_key=priv_key)
        if clusters_resp.status_code != 200:
            raise mr.RequestError(clusters_resp) # TODO
        c = []
        for result in clusters_resp.json()['results']:
            cluster_data = [result[key] for key in keys]
            c.append(cluster_data)
        clusters.extend(c)
    return clusters

def get_idle_clusters(pub_key: str, priv_key: str, clusters: list[tuple[str]]=[], threshold: int=48) -> list[str]:
    '''retrieves clusters that have not been queried within the past given threshold in hours (default 2 days)'''
    if not clusters:
        clusters = get_clusters(pub_key=pub_key, priv_key=priv_key, keys=['name','groupId'])
    idle_clusters = []
    for cluster, project in clusters: # type: ignore
        logs = mr.get(f"https://cloud.mongodb.com/api/atlas/v2/groups/{project}/dbAccessHistory/clusters/{cluster}", 
                      pub_key=pub_key, priv_key=priv_key).json()['accessLogs']
        timestamps = [datetime.strptime(log['timestamp'], '%a %b %d %H:%M:%S %Z %Y') for log in logs]
        now = datetime.utcnow()
        if not timestamps:
            idle_clusters.append(cluster)
        else:
            most_recent = min(timestamps)
            time_diff = now - most_recent
            hours_passed = time_diff.seconds // 3600
            if hours_passed >= threshold:
                idle_clusters.append(cluster)
    return idle_clusters

def pause_cluster(pub_key: str, priv_key: str, cluster_id: str):
    pass
