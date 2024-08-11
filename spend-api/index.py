from flask import Flask, request, jsonify
app = Flask(__name__)

'''
{startDate: -,
 endDate: -,
 org: -,
 projects: ?,
 clusters: ?,
 services: ?}
'''
required = ['startDate','endDate','org']
optional = ['projects','clusters','services']
@app.route("/spend/services", methods=['POST'])
def get_spend_by_service():
    payload = request.get_json()
    if not (set(payload.keys()) <= set(required+optional)):
        return 'Invalid Attribute(s) Specified', 400
    if not (set(required) <= set(payload.keys())):
        return 'Required Attribute(s) Not Specified', 400
    print(request.get_json()) 
    return '', 200

