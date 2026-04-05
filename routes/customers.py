
from datetime import datetime

from flask import render_template, request, redirect, flash
from db import rental_data, customer_data, STATUS

def init_customers_routes(app):
    
    @app.route('/customers')
    def customers_list():    

        search_query = request.args.get('search', '').lower()

        filtered_customers = []
        for c in customer_data:
            match_name = search_query in c['name'].lower()
            match_email = search_query in c['email'].lower()

            if match_name or match_email:
                filtered_customers.append(c)
        

        return render_template(
            'customer/list.html', 
            customers=filtered_customers,
            search_query=search_query   
    )

    @app.route('/customers/<int:item_id>')
    def delete_customer(item_id):
        # We need to use 'global' to modify the mock database list
        global customer_data 

        for r in rental_data:
            if r['customer_id'] == item_id and r["status"] == STATUS.ACTIVE:
                flash(f"Customer '{item_id}' have an active rentals, Can't be Deleted", "danger")
                return redirect('/customers')
        # Keep only the items that DO NOT match the deleted ID
        
        customer_data = [item for item in customer_data if item['id'] != item_id]
        
        flash(f"Customer '{item_id}' has been Deleted successfuly", "success")

        # Send the user back to the updated list
        return redirect('/customers')

    @app.route('/customers/new', methods=['GET', 'POST'])
    def new_customer():
        if request.method == 'POST':
            # 1. Capture the data immediately into a dict
            # This "mocks" an item object so the template can refill the fields
            form_data = {
                'id':  int(request.form.get('id')),
                'name': request.form.get('name'),
                'email': request.form.get('email'),
                'phone': request.form.get('phone'),
                'created_at': datetime.now().isoformat()
            }

            try:
                
                new_item = form_data
                for c in customer_data:
                    if c['email'].lower() == form_data['email'].lower():
                        flash(f"Email already exist ", "danger")
                        return render_template('customer/form.html', item=new_item)
                customer_data.append(new_item)
                flash(f"Successfully added {new_item['name']}!", "success")
                return redirect('/customers')

            except ValueError:
                flash("Please enter valid numbers for rate and quantity.", "danger")
                return render_template('customers/form.html', item=form_data)

        return render_template('customer/form.html', item=None)
