from flask import Flask, request, jsonify
app = Flask(__name__)

@app.route("/spend", methods=['POST'])
def get_spend():
    print(request.get_json()) 
    return '', 202

