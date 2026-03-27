from flask import Flask, render_template
from routes.api import init_api
from db import equipment_data, customer_data, rental_data, STATUS

app = Flask(__name__)

# Initialize API routes
init_api(app)

@app.route('/')
def index():
    counts = {
        'equipment': len(equipment_data),
        'customers': len(customer_data),
        'rentals': len(rental_data),
        'active_rentals': len([r for r in rental_data if r['status'] == STATUS.ACTIVE.value])
    }
    return render_template('index.html', counts=counts)

if __name__ == '__main__':
    app.run(debug=True)
