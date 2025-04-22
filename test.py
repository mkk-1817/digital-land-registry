from werkzeug.security import generate_password_hash
from pymongo import MongoClient

# Connect using pymongo
client = MongoClient("mongodb+srv://karthikmakkam:mkk_1817@project.e5qxv.mongodb.net/?retryWrites=true&w=majority&appName=Project")

# Select the correct database
db = client['digital_land_registry']

# Create the admin user
admin_user = {
    'email': 'admin@example.com',
    'password': generate_password_hash('admin123'),  # Strong password recommended!
    'role': 'admin'
}

# Check if admin already exists
existing = db.users.find_one({'email': admin_user['email']})
if existing:
    print("Admin user already exists.")
else:
    db.users.insert_one(admin_user)
    print("Admin user created.")
