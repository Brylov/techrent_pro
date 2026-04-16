from flask import Flask
from flasgger import Swagger
from routes.api import init_api

app = Flask(__name__)
app.secret_key = 'some_super_secret_hex_code_here'
# Custom configuration to match your 'Base URL' and 'v1.0.0' demo screen
swagger_config = {
    "headers": [],
    "specs": [
        {
            "endpoint": 'apispec_1',
            "route": '/apispec_1.json',
            "rule_filter": lambda rule: True,
            "model_filter": lambda tag: True,
        }
    ],
    "static_url_path": "/flasgger_static",
    "swagger_ui": True,
    "specs_route": "/api/docs"  # This sets the URL to http://localhost:5000/api/docs
}

template = {
    "swagger": "2.0",
    "info": {
        "title": "TechRent Pro REST API",
        "description": "Base URL: http://localhost:5000/api",
        "version": "1.0.0",
    }
}

swagger = Swagger(app, config=swagger_config, template=template)
# Initialize API routes
init_api(app)


if __name__ == '__main__':
    app.run(debug=True)
