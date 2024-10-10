from . import mongo_requests as mr

def get_cluster_stats(project_id, cluster_name, pub_key, priv_key):
    url = f"https://cloud.mongodb.com/api/atlas/v2/groups/{project_id}/clusters/{cluster_name}/stats"
    response = mr.get(url, pub_key=pub_key, priv_key=priv_key)
    if response.status_code != 200:
        raise mr.RequestError(response)
    return response.json()

def adjust_cluster_size(project_id, cluster_name, pub_key, priv_key, new_size):
    url = f"https://cloud.mongodb.com/api/atlas/v2/groups/{project_id}/clusters/{cluster_name}"
    payload = {"providerSettings": {"instanceSizeName": new_size}}
    response = mr.patch(url, data=payload, pub_key=pub_key, priv_key=priv_key)
    if response.status_code != 200:
        raise mr.RequestError(response)
    return response.json()

def auto_scale_cluster(project_id, cluster_name, pub_key, priv_key, scale_up_threshold, scale_down_threshold):
    stats = get_cluster_stats(project_id, cluster_name, pub_key, priv_key)
    cpu_usage = stats['processes'][0]['cpu']['usage']

    if cpu_usage > scale_up_threshold:
        adjust_cluster_size(project_id, cluster_name, pub_key, priv_key, new_size="M30")
    elif cpu_usage < scale_down_threshold:
        adjust_cluster_size(project_id, cluster_name, pub_key, priv_key, new_size="M10")

# Example usage:
# auto_scale_cluster('project_id', 'cluster_name', 'public_key', 'private_key', scale_up_threshold=70, scale_down_threshold=20)

INSTANCE_PRICES = {
    "M10": 0.08,   # $0.08 per hour
    "M20": 0.20,   # $0.20 per hour
    "M30": 0.60,   # $0.60 per hour
}



## Possible Savings in dashboard for automated cluster scaling.

def get_current_cluster_size(project_id, cluster_name, pub_key, priv_key):
    url = f"https://cloud.mongodb.com/api/atlas/v2/groups/{project_id}/clusters/{cluster_name}"
    response = mr.get(url, pub_key=pub_key, priv_key=priv_key)
    if response.status_code != 200:
        raise mr.RequestError(response)
    return response.json()['providerSettings']['instanceSizeName']

def calculate_savings(project_id, cluster_name, pub_key, priv_key, proposed_size):
    current_size = get_current_cluster_size(project_id, cluster_name, pub_key, priv_key)
    current_price = INSTANCE_PRICES.get(current_size, 0)
    proposed_price = INSTANCE_PRICES.get(proposed_size, 0)

    if current_price and proposed_price:
        hourly_savings = current_price - proposed_price
        monthly_savings = hourly_savings * 24 * 30  # Assuming 24/7 operation for 30 days
        return round(monthly_savings, 2)
    else:
        return 0.0


