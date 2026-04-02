from flask import render_template
from db import equipment_data, customer_data, rental_data, STATUS
from routes.equipment import init_equipment_routes

ITEMS_PER_PAGE = 5

def init_api(app):
    
    init_equipment_routes(app)
    
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

    
    
    