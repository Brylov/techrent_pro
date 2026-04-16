
Your **README.md** content is provided below in Markdown format. You can copy and paste this directly into a file named `README.md` in your project's root directory.

**Markdown**

```



# TechRent Pro – Inventory & Rental Management System

TechRent Pro is a robust, lightweight RESTful API and web application built with **Flask**. It is designed for managing a fleet of technical equipment, tracking customer registrations, and handling complex rental transactions with automated cost calculation and collision detection.

## 🚀 Key Features

### 🛠 Equipment Management
- **Full CRUD**: Create, Read, Update, and Delete inventory items.
- **Advanced Filtering**: Filter by category and search across names/descriptions.
- **Smart Stock Tracking**: Real-time availability calculation based on physical quantity minus active rentals.
- **Pagination**: Efficiently browse large inventories (5 items per page).

### 👥 Customer Directory
- **Registration**: Track client names, emails, and phone numbers.
- **Validation**: Prevents duplicate email and ID registrations.
- **Data Integrity**: Built-in "Foreign Key" protection—prevents deleting customers who have active rentals.

### 📈 Rental & Analytics
- **Transaction Engine**: Automated rental creation with date-overlap checking (prevents double-booking).
- **Cost Calculation**: Server-side logic to calculate total rental costs based on equipment daily rates.
- **Reports Dashboard**: 
    - Real-time revenue summary (Completed vs. Pipeline).
    - Top 3 Most-Rented Equipment analysis.
    - Top 3 Customers by spend.
    - Rental status distribution visualization.

### 📚 API Documentation (Swagger)
- Interactive API docs powered by **Flasgger**.
- Grouped endpoints for Equipment, Customers, Rentals, and Dashboard.
- **Try it out** functionality directly from the browser at `/api/docs`.

---

## 🛠 Tech Stack

- **Backend**: Python 3.x, Flask
- **Frontend**: Jinja2 Templates, Tailwind CSS
- **API Docs**: Swagger (Flasgger/OpenAPI)
- **Data**: Mock persistence via modular Python dictionaries (JSON-ready)

---

## 📂 Project Structure

```text
techrent_pro/
├── app.py              # Application factory and Swagger config
├── api.py              # Main API wrapper, dashboard routes, and filters
├── db.py               # Central data store (Equipment, Customers, Rentals)
├── routes/
│   ├── equipment.py    # Inventory endpoints
│   ├── customers.py    # Client management
│   └── rentals.py      # Transaction logic
├── templates/          # Jinja2 HTML templates
├── static/             # Static assets (if any)
└── .gitignore          # Production-ready file exclusion
```

---

## ⚙️ Installation & Setup

1. **Clone the repository** :
   **Bash**

```
   git clone https://github.com/Brylov/techrent_pro.git
   cd techrent_pro
```

1. **Create a Virtual Environment** :
   **Bash**

```
   python -m venv .venv
   source .venv/bin/activate  # Windows: .venv\Scripts\activate
```

1. **Install Dependencies** :
   **Bash**

```
   pip install -r requirenments.txt
```

1. **Run the Application** :
   **Bash**

```
   python app.py
```

1. **Access the App** :

* **Web Interface** : `http://localhost:5000`
* **API Docs** : `http://localhost:5000/api/docs`

---

## 🧪 API Usage Notes

* **DELETE Requests** : Delete operations use the `DELETE` HTTP method. The server returns a JSON object containing a redirect URL to ensure Flash messages persist across the client-side fetch.
* **Pagination** : Use query parameters for the equipment list: `/equipment?page=2&category=audio`.
* **Status Enum** : Rentals use a status enumeration: `ACTIVE`, `RETURNED`, `OVERDUE`.


---
## 📈 Next Steps (Roadmap)

While the project is currently fully functional in a development environment, the following improvements are planned for future versions:

### 1. Tailwind CSS Production Optimization
- **Current State**: Using Play CDN for rapid development.
- **Goal**: Transition to the Tailwind CLI build process to purge unused CSS classes and minify the final stylesheet for faster production load times. The shift requires Node.js server.

### 2. Environment Security
- **Goal**: Move sensitive configurations (like `SECRET_KEY`) out of the source code and into a `.env` file using `python-dotenv`.
- **Status**: Added to `.gitignore` in preparation for this shift.

### 3. Persistent Database
- **Current State**: Mock data stored in Python dictionaries (resets on restart).
- **Goal**: Integrate SQLAlchemy with a SQLite or PostgreSQL database to ensure data persists between application restarts.

### 4. Containerization (Future)
- **Goal**: Once the fundamentals of container orchestration are mastered, a `Dockerfile` and `docker-compose.yml` will be added to ensure the application environment is perfectly reproducible across any server.
---

---

## 📄 License

Created for TechRent Pro Management. © 2026 All rights reserved.
