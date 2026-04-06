from flask import jsonify, render_template, request, redirect, flash
from datetime import datetime
from db import equipment_data, rental_data, customer_data, STATUS


def init_rentals_routes(app):
    
    @app.route('/rentals')
    def rentals_list():
        selected_status = request.args.get('status', 'all').lower()

        unique_statuses = list(STATUS)
        
        filtered_rental = []
        for item in rental_data:

            item_status_str = item['status'].name.lower()
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
            statuses=unique_statuses,     # The dynamic dropdown list
            selected_status=selected_status, # To keep the dropdown selected
    )

    @app.route('/rentals/<int:rental_id>/return')
    def rental_return(rental_id):       
        global rental_data

        for index, r  in enumerate(rental_data):
            if r['id'] == rental_id:
                if r['status'] == STATUS.RETURNED:
                    flash("Can't return a returned item", "danger")
                    return redirect('/rentals')
                rental_data[index]['status'] = STATUS.RETURNED
                flash("Item Change to returned", "success")
                return redirect('/rentals')
        flash("Error occured couldn't change status", "danger")
        return redirect('/rentals')
    

    @app.route('/rentals/new', methods=['GET', 'POST'])
    def new_rental():
        # 1. Filter Equipment that is marked 'available'
        # In a real app, you'd also check if quantity > active rentals here
        available_equipment = [e for e in equipment_data if e.get('available')]

        if request.method == 'POST':
            form_data = {
                'customer_id': request.form.get('customer_id'),
                'equipment_id': request.form.get('equipment_id'),
                'start_date': request.form.get('start_date'),
                'end_date': request.form.get('end_date'),
            }

            try:
                # 2. Date Validation
                start_dt = datetime.fromisoformat(form_data['start_date'])
                end_dt = datetime.fromisoformat(form_data['end_date'])

                if end_dt <= start_dt:
                    flash("End date must be after the start date.", "danger")
                    return render_template('rentals/form.html', item=form_data, 
                                        customers=customer_data, equipment=available_equipment)

                # 3. Double-Booking Validation
                # Check if THIS equipment is already booked during these dates
                equip_id = int(form_data['equipment_id'])
                for r in rental_data:
                    if r['equipment_id'] == equip_id and r['status'] != STATUS.RETURNED:
                        r_start = datetime.fromisoformat(r['start_date'])
                        r_end = datetime.fromisoformat(r['end_date'])
                        
                        # Logic: (StartA <= EndB) and (EndA >= StartB)
                        if (start_dt <= r_end) and (end_dt >= r_start):
                            flash("This equipment is already booked for the selected dates.", "danger")
                            return render_template('rentals/form.html', item=form_data, 
                                                customers=customer_data, equipment=available_equipment)

                # 4. Calculate Total Cost
                selected_equip = next(e for e in equipment_data if e['id'] == equip_id)
                days = (end_dt - start_dt).days
                total_cost = days * selected_equip['daily_rate']

                # 5. Create Rental
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
                flash("Rental created successfully!", "success")
                return redirect('/rentals')

            except (ValueError, TypeError):
                flash("Please fill in all fields correctly.", "danger")

        return render_template('rentals/form.html', item=None, 
                            customers=customer_data, equipment=available_equipment)
        
                
        

        
    