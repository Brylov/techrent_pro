from flask import jsonify
from db import equipment_data

def init_api(app):
    @app.route('/api/equipment', methods=['GET'])
    def get_equipment_count():
        return jsonify({"count": len(equipment_data)})
