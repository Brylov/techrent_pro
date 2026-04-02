from flask import jsonify, render_template, request, redirect, flash
import math
from db import equipment_data, rental_data, customer_data, STATUS

ITEMS_PER_PAGE = 5

def init_equipment_routes(app):
    
    @app.route('/equipment')
    def equipment_list():
        selected_category = request.args.get('category', 'all').lower()
        search_query = request.args.get('search', '').lower()
        
        # Safely get the page number from the URL, default to 1
        try:
            page = int(request.args.get('page', 1))
        except ValueError:
            page = 1

        unique_categories = sorted(list(set(item['category'].title() for item in equipment_data)))

        filtered_equipment = []
        for item in equipment_data:
            match_category = (selected_category == 'all' or item['category'].lower() == selected_category)
            match_search = (search_query in item['name'].lower() or search_query in item['description'].lower())
            
            if match_category and match_search:
                filtered_equipment.append(item)

        # --- Pagination Logic ---
        total_items = len(filtered_equipment)
        total_pages = max(1, math.ceil(total_items / ITEMS_PER_PAGE))
        
        # Ensure page doesn't go out of bounds
        if page < 1: page = 1
        if page > total_pages: page = total_pages

        # Slice the list for the current page
        start_idx = (page - 1) * ITEMS_PER_PAGE
        end_idx = start_idx + ITEMS_PER_PAGE
        paginated_equipment = filtered_equipment[start_idx:end_idx]

        # 4. Pass everything to the template
        return render_template(
            'equipment/list.html', 
            equipment=paginated_equipment,     # The filtered list
            categories=unique_categories,     # The dynamic dropdown list
            selected_category=selected_category, # To keep the dropdown selected
            search_query=search_query,           # To keep the typed text in the bo
            page=page,                      # Pass current page
            total_pages=total_pages         # Pass total pages
    )

    @app.route('/equipment/<int:item_id>')
    def view_equipment(item_id):
        # 1. Find the specific equipment
        item = next((i for i in equipment_data if i['id'] == item_id), None)
        if not item:
            return "Equipment not found", 404
            
        # 2. Find all rentals for this specific equipment
        item_rentals = []
        active_rentals_count = 0
        
        for rental in rental_data:
            if rental['equipment_id'] == item_id:
                # Find the customer's name for this rental
                customer = next((c for c in customer_data if c['id'] == rental['customer_id']), None)
                customer_name = customer['name'] if customer else "Unknown Customer"
                
                # Check if it's currently active to calculate availability
                # (Adjust 'STATUS.ACTIVE' depending on how your db.py handles enums/strings)
                if rental['status'] in [STATUS.ACTIVE, STATUS.OVERDUE]:
                    active_rentals_count += 1
                
                # Add the enriched data to our history list
                item_rentals.append({
                    'customer_name': customer_name,
                    'start_date': rental['start_date'],
                    'end_date': rental.get('end_date', '-'), # Default to '-' if ongoing
                    'status': rental['status'].name if hasattr(rental['status'], 'name') else rental['status'],
                    'cost': rental.get('total_cost', 0) # Adjust key based on your db.py
                })
                
        # 3. Calculate currently available stock
        currently_available = item['quantity'] - active_rentals_count

        return render_template(
            'equipment/detail.html', 
            item=item,
            currently_available=currently_available,
            rental_history=item_rentals
        )


    @app.route('/equipment/<int:item_id>/edit', methods=['GET', 'POST'])
    def edit_equipment(item_id):
        # 1. Find the existing item
        item = next((i for i in equipment_data if i['id'] == item_id), None)
        if not item:
            flash("Equipment not found.", "danger")
            return redirect('/equipment')

        if request.method == 'POST':
            # 2. Capture the submitted data into a dictionary (the "Sticky" data)
            form_data = {
                'id': item_id, # Keep the ID so the form knows which item we are talking about
                'name': request.form.get('name'),
                'category': request.form.get('category'),
                'description': request.form.get('description'),
                'daily_rate': request.form.get('daily_rate'),
                'quantity': request.form.get('quantity'),
                'available': 'available' in request.form
            }

            try:
                # 3. Validation Logic
                rate_val = float(form_data['daily_rate'] or 0)
                quant_val = int(form_data['quantity'] or 0)

                if rate_val < 0 or quant_val < 0:
                    flash("Daily rate and quantity cannot be negative!", "danger")
                    # Pass form_data back as 'item' to keep the fields filled
                    return render_template('equipment/form.html', item=form_data)

                # 4. Success: Update the actual item in the list
                item['name'] = form_data['name']
                item['category'] = form_data['category']
                item['description'] = form_data['description']
                item['daily_rate'] = rate_val
                item['quantity'] = quant_val
                item['available'] = form_data['available']

                flash(f"Updated '{item['name']}' successfully!", "success")
                return redirect(f'/equipment/{item_id}')

            except ValueError:
                flash("Please enter valid numbers for rate and quantity.", "danger")
                return render_template('equipment/form.html', item=form_data)

        # GET request: Show form with original data
        return render_template('equipment/form.html', item=item)


    @app.route('/equipment/<int:item_id>/delete')
    def delete_equipment(item_id):
        # We need to use 'global' to modify the mock database list
        global equipment_data 
        
        # Keep only the items that DO NOT match the deleted ID
        equipment_data = [item for item in equipment_data if item['id'] != item_id]
        
        flash(f"Deleted item number '{item_id}' successfully!", "success")
        
        # Send the user back to the updated list
        return redirect('/equipment')

    @app.route('/equipment/new', methods=['GET', 'POST'])
    def new_equipment():
        if request.method == 'POST':
            # 1. Capture the data immediately into a dict
            # This "mocks" an item object so the template can refill the fields
            form_data = {
                'name': request.form.get('name'),
                'category': request.form.get('category'),
                'description': request.form.get('description'),
                'daily_rate': request.form.get('daily_rate'),
                'quantity': request.form.get('quantity'),
                'available': 'available' in request.form
            }

            try:
                rate_val = float(form_data['daily_rate'] or 0)
                quant_val = int(form_data['quantity'] or 0)
                
                # 2. Validation Logic
                if rate_val < 0 or quant_val < 0:
                    flash("Rates and quantities cannot be negative!", "danger")
                    # Pass form_data back as 'item' so the fields stay filled!
                    return render_template('equipment/form.html', item=form_data)

                # 3. If valid, proceed to save
                new_id = (max(item['id'] for item in equipment_data) + 1) if equipment_data else 101
                
                new_item = {
                    'id': new_id,
                    **form_data, # Spreads the strings from form_data
                    'daily_rate': rate_val, # Overwrites with actual numbers
                    'quantity': quant_val
                }
                
                equipment_data.append(new_item)
                flash(f"Successfully added {new_item['name']}!", "success")
                return redirect('/equipment')

            except ValueError:
                flash("Please enter valid numbers for rate and quantity.", "danger")
                return render_template('equipment/form.html', item=form_data)

        return render_template('equipment/form.html', item=None)