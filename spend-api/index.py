from flask import Flask, request, jsonify
import mongo_data as md
app = Flask(__name__)

'''
{startDate: -,
 endDate: -,
 org: -,
 projects: ?,
 clusters: ?,
 services: ?
 grouping: ?(organizations/clusters/projects/services)}
'''
required = ['startDate','endDate','org']
optional = ['projects','clusters','services', 'grouping']
@app.route("/spend", methods=['POST'])
def get_spend_by_service():
    payload = request.get_json()
    auth = request.authorization
    if not (set(payload.keys()) <= set(required+optional)):
        return 'Invalid Attribute(s) Specified', 400
    if not (set(required) <= set(payload.keys())):
        return 'Required Attribute(s) Not Specified', 400
    if not auth:
        return 'Authorization Header Expected', 401
    if str(auth).split()[0] != 'Basic' or auth.username is None or auth.password is None:
        return 'Invalid Authorization Header', 401
    try:
        print(payload)
        cost_breakdown = md.get_cost_details(pub_key=auth.username,
                                             priv_key=auth.password,
                                             start_date=payload['startDate'],
                                             end_date=payload['endDate'],
                                             org_id=payload['org'],
                                             projects=payload['projects'] if 'projects' in payload else [],
                                             clusters=payload['clusters'] if 'clusters' in payload else [],
                                             services=payload['services'] if 'services' in payload else [],
                                             group_by=payload['grouping'] if 'grouping' in payload else md.GROUP_BY_SERVICE)
        return cost_breakdown, 200
    except md.RequestError as e:
        return e.msg, e.code

@app.route("/savings", methods=['POST'])
def get_savings():
    payload = request.get_json()
    auth = request.authorization
    if len(payload.keys()) > 3:
        return 'Invalid Attribute(s) Specified', 400
    if len(payload.keys()) < 3 or not ('startDate' in payload.keys() and 'endDate' in payload.keys() and 'org' in payload.keys()):
        return 'Required Attribute(s) Not Specified', 400
    if not auth:
        return 'Authorization Header Expected', 401
    if str(auth).split()[0] != 'Basic' or auth.username is None or auth.password is None:
        return 'Invalid Authorization Header', 401
    try:
        idle_clusters = md.get_idle_clusters(pub_key=auth.username, priv_key=auth.password)
        cost_details = md.get_cost_details(pub_key=auth.username, priv_key=auth.password,
                                   start_date=payload['startDate'], end_date=payload['endDate'],
                                   org_id=payload['org'], clusters=[cluster_data['id'] for cluster_data in idle_clusters],
                                   group_by=md.GROUP_BY_CLUSTER)
        total_cost = 0
        for i in range(len(idle_clusters)):
            cluster_data = idle_clusters[i]
            try:
                cluster_data['cost'] = cost_details[cluster_data['id']]['usageAmount']
            except KeyError:
                cluster_data['cost'] = 0.0
            total_cost += cluster_data['cost']
        return {"idleClusters" : {"total" : total_cost,
                              "clusters" : idle_clusters},
                }, 200
    except md.RequestError as e:
        return e.msg, e.code

@app.route("/pause", methods=['POST'])
def pause_cluster():
    payload = request.get_json()
    auth = request.authorization
    if len(payload.keys()) > 1:
        return 'Invalid Attribute(s) Specified', 400
    if not payload.keys() or payload.keys()[0] != 'clusters':
        return 'Required Attribute(s) Not Specified', 400
    if not auth:
        return 'Authorization Header Expected', 401
    if str(auth).split()[0] != 'Basic' or auth.username is None or auth.password is None:
        return 'Invalid Authorization Header', 401
    return '', 200
