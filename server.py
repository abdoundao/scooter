from flask import Flask, jsonify
import json
import os

app = Flask(__name__)
detail_json_dir = "detail_json"
without_detail_json_dir = "without_detail_json"

@app.route('/detail/<int:id>', methods=['GET'])
def get_json(id):
    json_file = os.path.join(detail_json_dir, "referentiel_info_detail_%s.json" % id)
    if os.path.exists(json_file):
        with open(json_file, 'r') as f:
            data = json.load(f)
            return data
    else:
        return jsonify({"error": "ID non trouvé"}), 404

@app.route('/without_detail/<int:id>', methods=['GET'])
def get_without_json(id):
    json_file = os.path.join(without_detail_json_dir, "referentiel_info_detail_%s.json" % id)
    if os.path.exists(json_file):
        with open(json_file, 'r') as f:
            data =  json.load(f)
            return jsonify(data)
    else:
        return jsonify({"error": "ID non trouvé"}), 404

if __name__ == '__main__':
    app.run(debug=True)
