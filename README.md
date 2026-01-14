# Grocery Store Web Application

## Project Overview
The **Grocery Store Web Application** is a full-stack web project built using **Python Flask**, **MySQL**, and **HTML/CSS/JavaScript**. It simulates an online grocery store where users can browse products, manage their shopping cart, and place orders. An **admin panel** allows administrators to manage products, customers, and orders efficiently.  

This project demonstrates skills in **web development, database management, and cloud deployment**, making it suitable for portfolios, resume projects, or live demonstrations.

## Features

### Admin Panel
- Secure login and authentication  
- Add, edit, and delete products  
- View and manage customer orders  
- Dashboard showing store statistics and order summaries  

### Customer Panel
- User registration and login  
- Browse products by categories  
- Add items to cart and place orders  
- View order history and order status  

### Technical Highlights
- **Backend:** Python Flask (RESTful API, MVC structure)  
- **Database:** MySQL (connected via `mysql-connector-python`)  
- **Frontend:** HTML, CSS, JavaScript, Bootstrap  
- **Production Server:** Gunicorn for handling multiple requests  
- **Deployment:** Compatible with **Render** and **Google Cloud Run**  
- **Responsive Design:** Works across desktops and mobile devices  

---

## Installation & Setup

1.
  Clone the repository:

git clone https://github.com/yourusername/grocery-store.git
cd grocery-store

2.
Install Python dependencies:
pip install -r requirements.txt

3.
Set up MySQL database:
Create a database named grocery_store
Import SQL schema if provided or create tables manually
Configure database connection in db.py:
Copy code
Python
conn = mysql.connector.connect(
    host="localhost",
    user="your_db_user",
    password="your_db_password",
    database="grocery_store"
)


5.
Run the Flask application:

python app.py


6.
 Access the application in your browser:


http://localhost:5000
___________________________________________________________________________________
Usage
Admin login to manage products, orders, and users
Customers can register, login, browse products, add to cart, and place orders
Orders are stored in MySQL and can be viewed in the admin panel.
___________________________________________________________________________________
Project Structure
grocery_store/
│
├── app.py             # Main Flask application
├── db.py              # Database connection and queries
├── requirements.txt   # Python dependencies
├── templates/         # HTML templates (Jinja2)
├── static/            # CSS, JavaScript, images
├── README.md          # Project documentation
└── __pycache__/       # Compiled Python files
___________________________________________________________________________________
Deployment
This project can be deployed on Render or Google Cloud Run for live access.
Dockerfile included for containerized deployment
Environment variable PORT is set for cloud hosting
Gunicorn serves the app in production
___________________________________________________________________________________
Steps for Render Deployment:
Create a new Web Service on Render
Connect your GitHub repository
Set Python environment and PORT environment variable
Deploy the service to get a live link accessible to anyone
___________________________________________________________________________________
Steps for Google Cloud Run:
Containerize the app using Docker
Push the container to Google Container Registry
Deploy via Cloud Run
Use the generated URL to share with friends
___________________________________________________________________________________
Author
Shivam Jadhav
BCA Student
Full-Stack Developer (Python | Flask | MySQL)
Data Analytics Enthusiast