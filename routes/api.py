from datetime import datetime
from collections import Counter
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

    @app.route('/reports')
    def reports_dashboard():
        # 1. Revenue Summary
        total_completed_revenue = sum(r.get('total_cost', 0) for r in rental_data if r['status'] == STATUS.RETURNED)
        active_pipeline_revenue = sum(r.get('total_cost', 0) for r in rental_data if r['status'] in [STATUS.ACTIVE, STATUS.OVERDUE])

        # 2. Top 3 Most-Rented Equipment
        # Count occurrences of equipment_id in rental_data
        equipment_counts = Counter(r['equipment_id'] for r in rental_data)
        top_equip_ids = equipment_counts.most_common(3)
        
        top_equipment = []
        for equip_id, count in top_equip_ids:
            item = next((e for e in equipment_data if e['id'] == equip_id), None)
            if item:
                top_equipment.append({'name': item['name'], 'count': count})

        # 3. Top 3 Customers by Spend
        customer_spend = Counter()
        for r in rental_data:
            customer_spend[r['customer_id']] += r.get('total_cost', 0)
        
        top_cust_ids = customer_spend.most_common(3)
        top_customers = []
        for cust_id, spend in top_cust_ids:
            cust = next((c for c in customer_data if c['id'] == cust_id), None)
            if cust:
                top_customers.append({'name': cust['name'], 'spend': spend})

        # 4. Rentals by Status (for the visual bar)
        total_rentals = len(rental_data) or 1 # prevent division by zero
        status_counts = {
            'RETURNED': len([r for r in rental_data if r['status'] == STATUS.RETURNED]),
            'ACTIVE': len([r for r in rental_data if r['status'] == STATUS.ACTIVE]),
            'OVERDUE': len([r for r in rental_data if r['status'] == STATUS.OVERDUE])
        }
        
        # Calculate percentages for CSS widths
        status_pct = {k: (v / total_rentals) * 100 for k, v in status_counts.items()}

        return render_template('reports.html',
            completed_rev=total_completed_revenue,
            active_rev=active_pipeline_revenue,
            top_equipment=top_equipment,
            top_customers=top_customers,
            status_pct=status_pct,
            status_counts=status_counts
        )
        
    
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