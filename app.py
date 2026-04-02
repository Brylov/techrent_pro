from flask import Flask, render_template
from routes.api import init_api

app = Flask(__name__)
app.secret_key = 'some_super_secret_hex_code_here'
# Initialize API routes
init_api(app)


if __name__ == '__main__':
    app.run(debug=True)
