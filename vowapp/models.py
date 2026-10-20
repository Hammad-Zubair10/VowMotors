from datetime import datetime

from flask import current_app
from flask_login import UserMixin
from itsdangerous import URLSafeTimedSerializer
from werkzeug.security import generate_password_hash, check_password_hash

from .extensions import db, login_manager


class Dealer(UserMixin, db.Model):
    """A dealership staff account. Logs in to add/edit/remove inventory."""

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(180), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    vehicles = db.relationship(
        'Vehicle', backref='dealer', lazy='dynamic', cascade='all, delete-orphan'
    )

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def get_reset_token(self):
        serializer = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
        return serializer.dumps(self.id, salt='password-reset')

    @staticmethod
    def verify_reset_token(token, max_age=3600):
        serializer = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
        try:
            dealer_id = serializer.loads(token, salt='password-reset', max_age=max_age)
        except Exception:
            return None
        return Dealer.query.get(dealer_id)


@login_manager.user_loader
def load_dealer(dealer_id):
    return Dealer.query.get(int(dealer_id))


class Vehicle(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    dealer_id = db.Column(db.Integer, db.ForeignKey('dealer.id'), nullable=False)

    year = db.Column(db.Integer, nullable=False)
    make = db.Column(db.String(60), nullable=False)
    model = db.Column(db.String(60), nullable=False)
    trim = db.Column(db.String(60))
    body_style = db.Column(db.String(30), nullable=False)  # Car, SUV, Truck, Commercial
    price = db.Column(db.Numeric(10, 2), nullable=False)
    mileage = db.Column(db.Integer, default=0)
    exterior_color = db.Column(db.String(40))
    transmission = db.Column(db.String(30))
    fuel_type = db.Column(db.String(30))
    vin = db.Column(db.String(32), unique=True)
    description = db.Column(db.Text)
    status = db.Column(db.String(12), default='available')  # available | sold
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    photos = db.relationship(
        'VehiclePhoto', backref='vehicle', lazy='dynamic',
        order_by='VehiclePhoto.position', cascade='all, delete-orphan'
    )

    @property
    def title(self):
        parts = [str(self.year), self.make, self.model]
        if self.trim:
            parts.append(self.trim)
        return ' '.join(parts)

    @property
    def primary_photo(self):
        return self.photos.first()

    @property
    def is_sold(self):
        return self.status == 'sold'


class VehiclePhoto(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    vehicle_id = db.Column(db.Integer, db.ForeignKey('vehicle.id'), nullable=False)
    filename = db.Column(db.String(255), nullable=False)
    position = db.Column(db.Integer, default=0)


class ContactMessage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(180), nullable=False)
    phone = db.Column(db.String(30))
    subject = db.Column(db.String(150))
    message = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class FinancingApplication(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(180), nullable=False)
    phone = db.Column(db.String(30), nullable=False)
    employment_status = db.Column(db.String(40))
    annual_income = db.Column(db.String(40))
    down_payment = db.Column(db.String(40))
    vehicle_interest = db.Column(db.String(120))
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
