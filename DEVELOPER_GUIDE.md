# FinAccess Developer Guide

Welcome to the FinAccess Developer Guide! This document explains exactly how this application works under the hood from a software engineering perspective. By reading this, you will understand how all the moving parts connect, what each technology does, and how to replicate this architecture for your own future projects.

---

## 1. Architecture Overview (The Big Picture)

FinAccess follows a **Client-Server RESTful Architecture**. This means the frontend (what the user sees) and the backend (where data and logic live) are strictly separated. They talk to each other using HTTP requests and JSON data.

### The Tech Stack Breakdown
*   **Frontend (The Client):** HTML5, CSS3, Vanilla JavaScript.
    *   **HTML/CSS:** Defines the structure and look of the pages.
    *   **JavaScript (`fetch` API):** Runs in the user's browser, intercepts form submissions, sends HTTP requests to the backend, and dynamically updates the HTML based on the response.
*   **Backend (The Server):** Python & Flask.
    *   **Flask:** A lightweight web framework. It listens for incoming HTTP requests (like `POST /api/auth/login`) and routes them to the correct Python function.
    *   **Flask-JWT-Extended:** Handles security. It issues a cryptographic token (JWT) to users when they log in, ensuring only authorized users can access certain routes.
*   **Database Layer:** MySQL & Flask-SQLAlchemy.
    *   **MySQL:** A Relational Database Management System (RDBMS) that stores data in structured tables.
    *   **Flask-SQLAlchemy:** An Object-Relational Mapper (ORM). It allows Python code to talk to MySQL without writing raw SQL queries.
*   **Machine Learning Layer:** Scikit-Learn, Pandas, Numpy, SHAP.
    *   **Scikit-Learn:** Holds the trained Random Forest model (`model.pkl`) that predicts loan eligibility.
    *   **SHAP:** A mathematical tool that breaks down *why* the AI made a specific decision.

---

## 2. How the Application Works (The Lifecycle)

To understand the app, you must understand how data flows. Here is the lifecycle of a typical action, such as applying for a loan:

1.  **Serving the UI:** You visit `http://127.0.0.1:5000/apply`. Flask intercepts this, sees it's a page request, and simply returns the raw `apply.html` file.
2.  **User Action:** You fill out the loan form and click "Submit".
3.  **JavaScript Interception:** `main.js` stops the browser from doing a traditional page reload. It grabs your form data, formats it as JSON, grabs your JWT token from `localStorage`, and sends an asynchronous `POST` request to `/api/apply`.
4.  **Backend Processing:**
    *   Flask receives the request at the `/api/apply` route.
    *   It verifies your JWT token to ensure you are logged in.
    *   It passes the financial data to `ml/predict.py`.
5.  **Machine Learning:** `predict.py` loads `model.pkl`, generates a prediction (e.g., 85% approval), and uses SHAP to calculate the top positive and negative factors.
6.  **Database Storage:** The backend creates a new `Application` Python object with the inputs and the AI's result, and uses SQLAlchemy to save it to the MySQL database.
7.  **The Response:** Flask sends a JSON response back to the frontend: `{"status": "success", "result_id": 5}`.
8.  **DOM Update:** `main.js` receives this JSON and instantly redirects your browser to `/result/5`.

---

## 3. Database Concepts (Deep Dive)

The database is the memory of your application. Here is how FinAccess handles it using **SQLAlchemy (ORM)**.

### Relational Database Management System (RDBMS)
MySQL is relational. Data is stored in tables (like Excel spreadsheets) that relate to one another. 
*   **Primary Key (PK):** A unique ID for every row (e.g., User ID 1).
*   **Foreign Key (FK):** A column that links to the Primary Key of another table.

### Object-Relational Mapping (ORM)
Instead of writing SQL queries like `SELECT * FROM users WHERE email='x'`, we use an ORM. An ORM maps a Python `Class` to a Database `Table`. 

In `app/models/models.py`, we define our schema:

```python
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True) # Primary Key
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    
    # Relationship: One User can have Many Applications
    applications = db.relationship('Application', backref='user', lazy=True)

class Application(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False) # Foreign Key
    income = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(20)) # "Approved" or "Rejected"
```

### The CRUD Operations
Every web app does four basic database operations, known as CRUD. Here is how SQLAlchemy does them in this project:
1.  **Create (Insert):**
    ```python
    new_user = User(email="test@test.com", password_hash="hashed_pw")
    db.session.add(new_user)
    db.session.commit() # Actually writes to MySQL
    ```
2.  **Read (Select):**
    ```python
    user = User.query.filter_by(email="test@test.com").first()
    my_apps = Application.query.filter_by(user_id=current_user_id).all()
    ```
3.  **Update (Modify):**
    ```python
    user.email = "new@test.com"
    db.session.commit()
    ```
4.  **Delete (Remove):**
    ```python
    db.session.delete(user)
    db.session.commit()
    ```

---

## 4. File-by-File Breakdown

### The Root Directory
*   `run.py`: The entry point. You run `python run.py`. It imports the Flask app and calls `app.run()`.
*   `config.py`: Holds configuration variables (Database URI, JWT Secret Key).
*   `requirements.txt`: Lists all Python packages needed to run the project.

### `app/` (The Application Factory)
*   `__init__.py`: Initializes Flask, connects the Database, sets up JWT, and registers all the "Blueprints" (routing files).

### `app/models/` (Database Layer)
*   `models.py`: Contains the `User` and `Application` ORM classes. Also contains the password hashing logic using `Werkzeug`.

### `app/routes/` (The API Controllers)
*   `pages.py`: Very simple file. It catches URL requests (like `/login`, `/dashboard`) and sends back the raw HTML files from the `static/pages/` folder.
*   `auth.py`: Handles `/api/auth/register` and `/api/auth/login`. Returns JWT tokens.
*   `main.py`: Handles `/api/apply`, `/api/dashboard`, `/api/history`. Needs `@jwt_required()` so only logged-in users can use them.
*   `admin.py`: Handles `/api/admin/stats`. Checks if `current_user.is_admin` is True before returning data.

### `ml/` (The Brain)
*   `predict.py`: Loads the trained model, formats user inputs into a Pandas DataFrame, makes predictions, and generates SHAP values.
*   `model.pkl`: The serialized (saved) state of the trained Random Forest algorithm.

### `static/` (The Frontend)
*   `pages/*.html`: The raw HTML structure of every page. No logic, just structure.
*   `css/style.css`: The Ocean Theme stylesheet that makes everything look beautiful.
*   `js/main.js`: The heart of the frontend. Contains the `Auth` object (managing tokens), the `API` object (wrapping the `fetch` function), and event listeners that wait for you to submit forms.

---

## 5. How to Build Your Next Project Like This

If you want to build a completely new project (e.g., an E-Commerce site or a Student Management System) using this exact same architecture, follow these steps:

1.  **Design the Database (Models):**
    *   Start in `models.py`. Write out your classes (e.g., `Product`, `Order`, `Student`, `Course`). Decide the Primary Keys, Foreign Keys, and Relationships.
2.  **Build the REST API (Backend Routes):**
    *   Create a new file in `app/routes/` (e.g., `products.py`).
    *   Write the CRUD logic. Create an endpoint for `GET /api/products` (returns a JSON list of products) and `POST /api/products` (adds a new product to the DB).
3.  **Build the Static HTML (Frontend Structure):**
    *   Create `products.html` in `static/pages/`. Design the UI using standard CSS classes.
4.  **Connect them with JavaScript (Frontend Logic):**
    *   In `main.js`, add an event listener for when the `products.html` page loads.
    *   Use `fetch('/api/products')` to ask the backend for the data.
    *   Write a loop in JavaScript to generate HTML elements (`<div>Product Name</div>`) based on the JSON data you received, and inject it into the DOM using `document.getElementById('product-list').innerHTML`.

By strictly separating the **Data API** (Backend) from the **Visuals** (Frontend), your code remains incredibly organized, easily testable, and highly scalable.
