from flask import jsonify, render_template, request, redirect, flash
import math
from db import equipment_data, rental_data, customer_data, STATUS


def init_rentals_routes(app):
    
    @app.route('/rentals')
    def rentals_list():
        selected_status = request.args.get('status', 'all').lower()

        unique_statuses = list(STATUS)
        
        filtered_rental = []
        for item in rental_data:

            item_status_str = item['status'].name.lower() # Gets 'active' or 'returned'
            match_status = (selected_status == 'all' or item_status_str == selected_status)

            customer = next((c for c in customer_data if c['id'] == item['customer_id']), None)
            item['customer_name'] = customer['name'] if customer else "Unknown Customer"

            equipment = next((e for e in equipment_data if e['id'] == item['equipment_id']), None)
            item['equipment_name'] = equipment['name'] if equipment else "Unknown Equipment"
            
            if match_status:
                filtered_rental.append(item)

        # 4. Pass everything to the template
        return render_template(
            'rentals/list.html', 
            rental=filtered_rental,     # The filtered list
            customer=customer_data,
            statuses=unique_statuses,     # The dynamic dropdown list
            selected_status=selected_status, # To keep the dropdown selected
    )