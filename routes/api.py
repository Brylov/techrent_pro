from datetime import datetime

from flask import render_template
from db import equipment_data, customer_data, rental_data, STATUS
from routes.equipment import init_equipment_routes
from routes.customers import init_customers_routes
from routes.rentals import init_rentals_routes

def init_api(app):
    
    init_equipment_routes(app)
    init_customers_routes(app)
    init_rentals_routes(app)
    
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
    
    @app.template_filter('format_date')
    def format_date(value):
        if not value:
            return ""
        try:
            # 1. Convert the string to a datetime object
            # We split at '.' to ignore microseconds if they exist
            date_obj = datetime.fromisoformat(value.split('.')[0])
            # 2. Return the formatted string
            return date_obj.strftime('%d-%m-%Y')
        except (ValueError, TypeError):
            return value # Return original if it fails

    @app.template_filter('format_date_short')
    def format_date_short(value):
        if not value or value == '-':
            return "N/A"
        try:
            # Convert string to datetime (stripping microseconds if they exist)
            date_obj = datetime.fromisoformat(value.split('.')[0])
            # %b is short month (Jan, Feb...), %d is day (01, 02...)
            return date_obj.strftime('%b%d')
        except (ValueError, TypeError):
            return value