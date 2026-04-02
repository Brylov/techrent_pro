from flask import jsonify, render_template, request, redirect
import math
from db import equipment_data

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
        # Find the specific item in your mock database
        item = next((i for i in equipment_data if i['id'] == item_id), None)
        
        if not item:
            return "Equipment not found", 404
            
        # For now, just return a simple string to prove it works
        return f"<h1>Viewing Equipment: {item['name']} (ID: {item['id']})</h1>"


    @app.route('/equipment/<int:item_id>/edit')
    def edit_equipment(item_id):
        item = next((i for i in equipment_data if i['id'] == item_id), None)
        
        # For now, just a placeholder
        return f"<h1>Edit Screen for: {item['name']}</h1>"


    @app.route('/equipment/<int:item_id>/delete')
    def delete_equipment(item_id):
        # We need to use 'global' to modify the mock database list
        global equipment_data 
        
        # Keep only the items that DO NOT match the deleted ID
        equipment_data = [item for item in equipment_data if item['id'] != item_id]
        
        # Send the user back to the updated list
        return redirect('/equipment')
