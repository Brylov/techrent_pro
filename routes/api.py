from flask import jsonify, render_template
from db import equipment_data, customer_data, rental_data, STATUS

def init_api(app):
    
    @app.route('/')
    def index():
        counts = {
            'equipment': len(equipment_data),
            'customers': len(customer_data),
            'rentals': len(rental_data),
            'active_rentals': sum(1 for r in rental_data if r['status'] == STATUS.ACTIVE),
        }
        last_five_rentals = rental_data[-5:][::-1]
        
        return render_template('index.html', counts=counts, rentals=last_five_rentals)
    
    @app.route('/equipment', methods=['GET'])
    def equipment_list():
        return render_template('equipment/detail.html', equipment=equipment_data)
