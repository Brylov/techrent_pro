from flask import jsonify, render_template, request, redirect, flash, url_for
import math
from db import equipment_data, rental_data, customer_data, STATUS

ITEMS_PER_PAGE = 5

def init_equipment_routes(app):
    
    @app.route('/equipment')
    def equipment_list():
        """
        List and filter equipment with pagination.
        ---
        tags:
          - Equipment
        parameters:
          - name: category
            in: query
            type: string
            default: all
          - name: search
            in: query
            type: string
          - name: page
            in: query
            type: integer
            default: 1
        responses:
          200:
            description: Paginated list of equipment.
        """
        selected_category = request.args.get('category', 'all').lower()
        search_query = request.args.get('search', '').lower()
        
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

        total_items = len(filtered_equipment)
        total_pages = max(1, math.ceil(total_items / ITEMS_PER_PAGE))
        page = max(1, min(page, total_pages))

        start_idx = (page - 1) * ITEMS_PER_PAGE
        end_idx = start_idx + ITEMS_PER_PAGE
        paginated_equipment = filtered_equipment[start_idx:end_idx]

        return render_template(
            'equipment/list.html', 
            equipment=paginated_equipment,
            categories=unique_categories,
            selected_category=selected_category,
            search_query=search_query,
            page=page,
            total_pages=total_pages
        )
    @app.route('/equipment/<int:item_id>')
    def view_equipment(item_id):
        """
        Detailed view of a specific equipment item and its rental history.
        ---
        tags:
          - Equipment
        parameters:
          - name: item_id
            in: path
            type: integer
            required: true
        responses:
          200:
            description: Equipment details and rental history.
          404:
            description: Equipment not found.
        """
        item = next((i for i in equipment_data if i['id'] == item_id), None)
        if not item:
            return "Equipment not found", 404
            
        # Data Enrichment: Joining Rental data with Customer names
        item_rentals = []
        active_rentals_count = 0
        
        for rental in rental_data:
            if rental['equipment_id'] == item_id:
                customer = next((c for c in customer_data if c['id'] == rental['customer_id']), None)
                customer_name = customer['name'] if customer else "Unknown Customer"
                
                # Check status against Enum members to determine real-time availability
                if rental['status'] in [STATUS.ACTIVE, STATUS.OVERDUE]:
                    active_rentals_count += 1
                
                item_rentals.append({
                    'customer_name': customer_name,
                    'start_date': rental['start_date'],
                    'end_date': rental.get('end_date', '-'),
                    'status': rental['status'].name if hasattr(rental['status'], 'name') else rental['status'],
                    'cost': rental.get('total_cost', 0)
                })
                
        # Calculate stock: physical quantity minus units currently out on rent
        currently_available = item['quantity'] - active_rentals_count

        return render_template(
            'equipment/detail.html', 
            item=item,
            currently_available=currently_available,
            rental_history=item_rentals
        )

    @app.route('/equipment/<int:item_id>/edit', methods=['GET', 'POST'])
    def edit_equipment(item_id):
        """
        Update existing equipment attributes.
        ---
        tags:
          - Equipment
        parameters:
          - name: item_id
            in: path
            type: integer
            required: true
        responses:
          200:
            description: Edit form rendered.
          302:
            description: Redirect to details on success.
        """
        item = next((i for i in equipment_data if i['id'] == item_id), None)
        if not item:
            flash("Action failed: Equipment record missing.", "danger")
            return redirect(url_for('equipment_list'))

        if request.method == 'POST':
            # Collect data for 'sticky' form behavior in case of validation failure
            form_data = {
                'id': item_id,
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

                if rate_val < 0 or quant_val < 0:
                    flash("Input Error: Financial rates and stock quantities cannot be negative.", "danger")
                    return render_template('equipment/form.html', item=form_data)

                # Commit changes to the reference object in equipment_data
                item.update({
                    'name': form_data['name'],
                    'category': form_data['category'],
                    'description': form_data['description'],
                    'daily_rate': rate_val,
                    'quantity': quant_val,
                    'available': form_data['available']
                })

                flash(f"Success: Record for '{item['name']}' has been updated.", "success")
                return redirect(url_for('view_equipment', item_id=item_id))

            except ValueError:
                flash("Type Error: Please provide valid numerical values.", "danger")
                return render_template('equipment/form.html', item=form_data)

        return render_template('equipment/form.html', item=item)

    @app.route('/equipment/<int:item_id>/delete', methods=['DELETE'])
    def delete_equipment(item_id):
        """
        Permanently remove equipment from the inventory.
        ---
        tags:
          - Equipment
        description: >
          Deletes an equipment item by ID. This returns a JSON object 
          with a redirect URL.
        parameters:
          - name: item_id
            in: path
            type: integer
            required: true
            description: The unique ID of the equipment to be removed.
        responses:
          200:
            description: Item deleted successfully.
            schema:
              type: object
              properties:
                redirect:
                  type: string
                  example: "/equipment"
          404:
            description: Equipment ID not found.
        """
        global equipment_data
        equipment_data[:] = [item for item in equipment_data if item['id'] != item_id]
        flash(f"Inventory Update: Equipment #{item_id} removed successfully.", "success")
        return jsonify({"redirect": url_for('equipment_list')}), 200

    @app.route('/equipment/new', methods=['GET', 'POST'])
    def new_equipment():
        """
        Add new equipment to the fleet.
        ---
        tags:
          - Equipment
        responses:
          200:
            description: Registration form.
          302:
            description: Redirect to list on success.
        """
        if request.method == 'POST':
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
                
                if rate_val < 0 or quant_val < 0:
                    flash("Input Error: Rates and quantities must be positive values.", "danger")
                    return render_template('equipment/form.html', item=form_data)

                # ID Generation: Incremental logic for mock persistence
                new_id = (max(item['id'] for item in equipment_data) + 1) if equipment_data else 101
                
                new_item = {
                    'id': new_id,
                    **form_data,
                    'daily_rate': rate_val,
                    'quantity': quant_val
                }
                
                equipment_data.append(new_item)
                flash(f"Onboarding Complete: {new_item['name']} added to fleet.", "success")
                return redirect(url_for('equipment_list'))

            except ValueError:
                flash("Type Error: Numeric validation failed.", "danger")
                return render_template('equipment/form.html', item=form_data)

        return render_template('equipment/form.html', item=None)