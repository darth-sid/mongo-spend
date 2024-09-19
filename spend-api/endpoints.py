from flask import Flask, request, jsonify
import mongo_data as md
app = Flask(__name__)
resp_dict = {
        'no-auth': ('Authorization Header Expected', 401),
        'invalid-auth': ('Invalid Authorization Header', 401),
        'missing-args': ('Required Attribute(s) Not Specified', 400),
}

def _listify(value: str|list|None) -> list:
    if isinstance(value,list): return value
    return [value] 

def _check_auth(auth) -> tuple[str,int]|None:
    print(type(auth))
    if not auth:
        return resp_dict['no-auth']
    if str(auth).split()[0] != 'Basic' or auth.username is None or auth.password is None:
        return resp_dict['invalid-auth']
    return None


# /spend/month=[YYYY-MM]&org=[org_id]
# optional + repeatable: &project=[group_id]&cluster=[cluster_id]&service=[service]
# optional: &grouping=[grouping_type]
@app.route("/spend", methods=['GET'])
def get_spend_by_service():
    date = request.args.get('month')
    org = request.args.get('org')
    projects = _listify(request.args.get('project'))
    clusters = _listify(request.args.get('cluster'))
    services = _listify(request.args.get('service'))
    grouping = request.args.get('grouping')
    auth = request.authorization
    #check for valid auth
    if (resp:=_check_auth(auth)):
        return resp
    #check for required queries
    if date is None or org is None:
        return resp_dict['missing-args']

    year,month = date.split('-')
    start_date = '-'.join([year,month,'01'])
    end_date = '-'.join([year,str(int(month)+1).zfill(2),'01'])

    try:
        cost_breakdown = md.get_cost_details(pub_key=auth.username, #type: ignore
                                             priv_key=auth.password, #type: ignore
                                             start_date=start_date,
                                             end_date=end_date,
                                             org_id=org,
                                             projects=projects if projects is not None else [],
                                             clusters=clusters if clusters is not None else [],
                                             services=services if services is not None else [],
                                             group_by=grouping if grouping is not None else md.GROUP_BY_ORG)
        return cost_breakdown, 200
    except md.RequestError as e:
        return e.msg, e.code

# /cluster-size?clusterName=[cluster_name]&project=[group_id]
@app.route('/cluster-size',methods=['GET'])
def get_cluster_size():
    cluster = request.args.get('clusterName')
    project = request.args.get('project')
    auth = request.authorization
    #check for valid auth
    if (resp:=_check_auth(auth)):
        return resp
    #check for required queries
    if cluster is None or project is None:
        return resp_dict['missing-args']
    try:
        
        current_size = md.get_current_cluster_size(project_id=project,
                                                cluster_name=cluster,
                                                pub_key=auth.username, #type: ignore
                                                priv_key=auth.password) #type: ignore
        return jsonify({"current_size": current_size}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# /savings?startDate=[YYYY-MM-DD]&endDate=[YYYY-MM-DD]&org=[org_id]
@app.route("/savings/idle", methods=['GET'])
def get_savings():
    start_date = request.args.get('startDate')
    end_date = request.args.get('endDate')
    org = request.args.get('org')
    auth = request.authorization
    #check for valid auth
    if (resp:=_check_auth(auth)):
        return resp
    #check for required queries
    if start_date is None or end_date is None or org is None:
        return resp_dict['missing-args']

    try:
        idle_clusters = md.get_idle_clusters(pub_key=auth.username, priv_key=auth.password) #type: ignore
        cost_details = md.get_cost_details(pub_key=auth.username, priv_key=auth.password, #type: ignore
                                   start_date=start_date, end_date=end_date,
                                   org_id=org, clusters=[cluster_data['id'] for cluster_data in idle_clusters],
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

# /savings/scaling?clusterName=[cluster_name]&project=[group_id]&size=[tier]
@app.route('/savings/scaling', methods=['GET'])
def get_scaling_savings():
    cluster = request.args.get('clusterName')
    project = request.args.get('project')
    new_size = request.args.get('')
    auth = request.authorization
    #check for valid auth
    if (resp:=_check_auth(auth)):
        return resp
    #check for required queries
    if cluster is None or project is None or new_size is None:
        return resp_dict['missing-args']

    try:
        savings = md.calculate_savings(project_id=project,
                                    cluster_name=cluster,
                                       pub_key=auth.username, #type: ignore
                                    priv_key=auth.password, #type: ignore
                                    proposed_size=new_size)
        return jsonify({"savings": savings})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# /pause?clusterName=[cluster_name]&project=[group_id]
@app.route("/pause", methods=['POST'])
def pause_cluster():
    cluster = request.args.get('clusterName')
    project = request.args.get('project')
    auth = request.authorization
    #check for valid auth
    if (resp:=_check_auth(auth)):
        return resp
    #check for required queries
    if cluster is None or project is None:
        return resp_dict['missing-args']
    
    try:
        md.pause_cluster(pub_key=auth.username, #type: ignore
                         priv_key=auth.password, #type: ignore
                         cluster=cluster,
                         project=project)
        return '', 200
    except md.RequestError as e:
        return e.msg, e.code
