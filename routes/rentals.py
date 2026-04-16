from flask import render_template, request, redirect, flash, url_for, jsonify
from datetime import datetime
from db import equipment_data, rental_data, customer_data, STATUS

def init_rentals_routes(app):
    
    @app.route('/rentals', methods=['GET'])
    def rentals_list():
        """
        Fetch all rentals with relational data (Customer & Equipment names).
        ---
        tags:
          - Rentals
        parameters:
          - name: status
            in: query
            type: string
            default: all
            description: Filter by rental status (Active, Returned, Overdue).
        responses:
          200:
            description: List of enriched rental records.
        """
        selected_status = request.args.get('status', 'all').lower()
        unique_statuses = list(STATUS)
        
        filtered_rental = []
        for item in rental_data:
            # Normalize status for string comparison
            item_status_str = item['status'].name.lower()
            match_status = (selected_status == 'all' or item_status_str == selected_status)

            # Manual 'Join' logic: Injecting names into the rental object for template display
            # next() is used here for efficient O(1) matching in our mock data
            customer = next((c for c in customer_data if c['id'] == item['customer_id']), None)
            item['customer_name'] = customer['name'] if customer else "Unknown Customer"

            equipment = next((e for e in equipment_data if e['id'] == item['equipment_id']), None)
            item['equipment_name'] = equipment['name'] if equipment else "Unknown Equipment"

            if match_status:
                filtered_rental.append(item)

        return render_template(
            'rentals/list.html', 
            rental=filtered_rental,
            statuses=unique_statuses,
            selected_status=selected_status
        )

    @app.route('/rentals/<int:rental_id>/return')
    def rental_return(rental_id):
        """
        Process the return of a rented item.
        ---
        tags:
          - Rentals
        parameters:
          - name: rental_id
            in: path
            type: integer
            required: true
        responses:
          302:
            description: Redirects back to rentals list.
        """
        for r in rental_data:
            if r['id'] == rental_id:
                # Idempotency check: prevents re-processing already returned items
                if r['status'] == STATUS.RETURNED:
                    flash("Action Denied: This transaction is already closed.", "warning")
                    return redirect(url_for('rentals_list'))
                
                r['status'] = STATUS.RETURNED
                r['actual_return_date'] = datetime.now().isoformat()
                
                flash(f"Success: Rental #{rental_id} marked as returned.", "success")
                return redirect(url_for('rentals_list'))

        flash("Processing Error: Rental record not found.", "danger")
        return redirect(url_for('rentals_list'))

    @app.route('/rentals/new', methods=['GET', 'POST'])
    def new_rental():
        """
        Create a new rental transaction with availability and overlap checks.
        ---
        tags:
          - Rentals
        responses:
          200:
            description: New rental form or validation failure.
          302:
            description: Redirects to list on success.
        """
        # Master inventory check: only show equipment flagged as 'available'
        available_equipment = [e for e in equipment_data if e.get('available')]

        if request.method == 'POST':
            form_data = {
                'customer_id': request.form.get('customer_id'),
                'equipment_id': request.form.get('equipment_id'),
                'start_date': request.form.get('start_date'),
                'end_date': request.form.get('end_date'),
            }

            try:
                # Chronological Validation
                start_dt = datetime.fromisoformat(form_data['start_date'])
                end_dt = datetime.fromisoformat(form_data['end_date'])

                if end_dt <= start_dt:
                    flash("Scheduling Error: End date must occur after start date.", "danger")
                    return render_template('rentals/form.html', item=form_data, 
                                           customers=customer_data, equipment=available_equipment)

                # Collision Detection logic for the specific unit
                equip_id = int(form_data['equipment_id'])
                for r in rental_data:
                    if r['equipment_id'] == equip_id and r['status'] != STATUS.RETURNED:
                        r_start = datetime.fromisoformat(r['start_date'])
                        r_end = datetime.fromisoformat(r['end_date'])
                        
                        # Overlap logic: (StartA <= EndB) and (EndA >= StartB)
                        if (start_dt <= r_end) and (end_dt >= r_start):
                            flash("Inventory Conflict: This unit is already booked for the selected window.", "danger")
                            return render_template('rentals/form.html', item=form_data, 
                                                   customers=customer_data, equipment=available_equipment)

                # Server-side cost calculation to ensure integrity
                selected_equip = next(e for e in equipment_data if e['id'] == equip_id)
                days = (end_dt - start_dt).days or 1
                total_cost = days * selected_equip['daily_rate']

                # ID Generation for mock DB
                new_id = (max(r['id'] for r in rental_data) + 1) if rental_data else 5001
                new_rental = {
                    'id': new_id,
                    'customer_id': int(form_data['customer_id']),
                    'equipment_id': equip_id,
                    'start_date': form_data['start_date'],
                    'end_date': form_data['end_date'],
                    'total_cost': total_cost,
                    'status': STATUS.ACTIVE
                }

                rental_data.append(new_rental)
                flash(f"Transaction Complete: Rental #{new_id} generated.", "success")
                return redirect(url_for('rentals_list'))

            except (ValueError, TypeError):
                flash("Validation Error: Please verify all date and selection fields.", "danger")

        return render_template('rentals/form.html', item=None, 
                               customers=customer_data, equipment=available_equipment)