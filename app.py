import os
from flask import Flask, render_template, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

# 1. Fetch environment variables or use safe defaults
DB_HOST = os.getenv("MYSQL_HOST", "mysql-271ff5b2-pranesh26jha-6828.h.aivencloud.com")
DB_PORT = os.getenv("MYSQL_PORT", "12691") # Put your actual 5-digit Aiven port here
DB_USER = os.getenv("MYSQL_USER", "avnadmin")
DB_PASSWORD = os.getenv("MYSQL_PASSWORD", "")
DB_NAME = os.getenv("MYSQL_DB", "defaultdb")

# 2. Explicitly set SQLALCHEMY_DATABASE_URI using PyMySQL driver format with SSL
app.config['SQLALCHEMY_DATABASE_URI'] = (
    f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    f"?ssl_mode=REQUIRED"
)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# 3. Initialize SQLAlchemy
db = SQLAlchemy(app)

# Define your Model schema
class Booking(db.Model):
    __tablename__ = 'bookings'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    pickup = db.Column(db.String(255), nullable=False)
    drop_loc = db.Column(db.String(255), nullable=False)
    service = db.Column(db.String(255), nullable=False)
    weight = db.Column(db.String(100), nullable=False)
    pickup_date = db.Column(db.Date, nullable=False)
    remarks = db.Column(db.Text)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/bookings', methods=['POST'])
def create_booking():
    data = request.get_json()
    if not data:
        return jsonify({"status": "error", "message": "No data provided"}), 400

    try:
        from datetime import datetime
        p_date = datetime.strptime(data.get('date'), '%Y-%m-%d').date()

        new_booking = Booking(
            name=data.get('name'),
            phone=data.get('phone'),
            pickup=data.get('pickup'),
            drop_loc=data.get('drop'),
            service=data.get('service'),
            weight=data.get('weight'),
            pickup_date=p_date,
            remarks=data.get('remarks', '')
        )
        db.session.add(new_booking)
        db.session.commit()

        return jsonify({"status": "success", "message": "Booking saved successfully to Aiven database!"}), 201

    except Exception as e:
        db.session.rollback()
        print(f"Error saving booking: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True, port=5000)