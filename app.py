import os
from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__, template_folder='templates', static_folder='static')
CORS(app)

# Configure Database from .env
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Define Booking Model (Database Table)
class Booking(db.Model):
    __tablename__ = 'bookings'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    pickup_location = db.Column(db.String(255), nullable=False)
    drop_location = db.Column(db.String(255), nullable=False)
    service_type = db.Column(db.String(255), nullable=False)
    cargo_weight = db.Column(db.String(100), nullable=False)
    pickup_date = db.Column(db.String(50), nullable=False)
    remarks = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.TIMESTAMP, server_default=db.func.current_timestamp())

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'phone': self.phone,
            'pickup': self.pickup_location,
            'drop': self.drop_location,
            'service': self.service_type,
            'weight': self.cargo_weight,
            'date': self.pickup_date,
            'remarks': self.remarks,
            'created_at': str(self.created_at)
        }

# Create database tables automatically if they don't exist
with app.app_context():
    db.create_all()

# Route: Serve Frontend Homepage
@app.route('/')
def home():
    return render_template('index.html')

# API Route: Save Booking Request from Frontend JS
@app.route('/api/bookings', methods=['POST'])
def create_booking():
    try:
        data = request.get_json()

        new_booking = Booking(
            name=data.get('name'),
            phone=data.get('phone'),
            pickup_location=data.get('pickup'),
            drop_location=data.get('drop'),
            service_type=data.get('service'),
            cargo_weight=data.get('weight'),
            pickup_date=data.get('date'),
            remarks=data.get('remarks', 'कोई नहीं')
        )

        db.session.add(new_booking)
        db.session.commit()

        return jsonify({
            'success': True,
            'message': 'Booking saved successfully to database!',
            'bookingId': new_booking.id
        }), 201

    except Exception as e:
        db.session.rollback()
        print("❌ Database Error:", str(e))
        return jsonify({'success': False, 'message': 'Internal server error'}), 500

# API Route: Fetch All Bookings (for Admin Dashboard)
@app.route('/api/bookings', methods=['GET'])
def get_bookings():
    try:
        all_bookings = Booking.query.order_by(Booking.id.desc()).all()
        return jsonify({
            'success': True,
            'bookings': [b.to_dict() for b in all_bookings]
        }), 200
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    print(f"🚀 Express Logistics Server running on http://localhost:{port}")
    app.run(host='0.0.0.0', port=port, debug=True)