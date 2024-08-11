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
    except md.RequestError as e:
        print("!")
        return e.msg, e.code
    return cost_breakdown, 200

