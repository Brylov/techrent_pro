from datetime import datetime
from flask import render_template, request, redirect, flash, url_for, jsonify
from db import rental_data, customer_data, STATUS

def init_customers_routes(app):
    
    @app.route('/customers', methods=['GET'])
    def customers_list(): 
        """
        Retrieve and filter the customer directory.
        ---
        tags:
          - Customers
        parameters:
          - name: search
            in: query
            type: string
            description: Search by name or email (case-insensitive).
        responses:
          200:
            description: Customer list rendered successfully.
        """
        search_query = request.args.get('search', '').lower()

        filtered_customers = [
            c for c in customer_data 
            if search_query in c['name'].lower() or search_query in c['email'].lower()
        ]

        return render_template(
            'customer/list.html', 
            customers=filtered_customers,
            search_query=search_query   
        )

    @app.route('/customers/<int:item_id>', methods=['DELETE'])
    def delete_customer(item_id):
        """
        Remove a customer from the system.
        ---
        tags:
          - Customers
        parameters:
          - name: item_id
            in: path
            type: integer
            required: true
            description: Unique ID of the customer.
        responses:
          200:
            description: Returns a redirect instruction for the frontend.
            schema:
              type: object
              properties:
                redirect:
                  type: string
        """
        # Data Integrity: Prevent orphan rentals by checking for active contracts
        for r in rental_data:
            if r['customer_id'] == item_id and r["status"] == STATUS.ACTIVE:
                # We return JSON here too so the Fetch call can display the error
                flash(f"Constraint Error: Customer #{item_id} has active rentals.", "danger")
                return jsonify({"redirect": url_for('customers_list')}), 200

        # Maintain global list reference
        customer_data[:] = [item for item in customer_data if item['id'] != item_id]
        
        flash(f"Customer #{item_id} successfully purged from records.", "success")
        return jsonify({"redirect": url_for('customers_list')}), 200

    @app.route('/customers/new', methods=['GET', 'POST'])
    def new_customer():
        """
        Register a new customer.
        ---
        tags:
          - Customers
        parameters:
          - name: id
            in: formData
            type: integer
            required: true
          - name: name
            in: formData
            type: string
            required: true
          - name: email
            in: formData
            type: string
            required: true
        responses:
          200:
            description: Form rendered or validation error returned.
          302:
            description: Redirects to list on success.
        """
        if request.method == 'POST':
            try:
                form_data = {
                    'id': int(request.form.get('id')),
                    'name': request.form.get('name'),
                    'email': request.form.get('email'),
                    'phone': request.form.get('phone'),
                    'created_at': datetime.now().isoformat()
                }

                # Collision Check: Email
                if any(c['email'].lower() == form_data['email'].lower() for c in customer_data):
                    flash("Duplicate Error: Email already exists.", "danger")
                    return render_template('customer/form.html', item=form_data)

                # Collision Check: ID
                if any(c['id'] == form_data['id'] for c in customer_data):
                    flash("Duplicate Error: ID already assigned.", "danger")
                    return render_template('customer/form.html', item=form_data)

                customer_data.append(form_data)
                flash(f"Success: {form_data['name']} added.", "success")
                return redirect(url_for('customers_list'))

            except (ValueError, TypeError):
                flash("Input Error: Check your numeric values.", "danger")
                return render_template('customer/form.html', item=request.form)

        return render_template('customer/form.html', item=None)