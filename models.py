from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    travel_entry_id = db.Column(db.String(100), unique=True, nullable=False)
    tickets = db.relationship('Ticket', backref='user', lazy=True)

class Ticket(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    travel_entry_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    event_id = db.Column(db.String(100), nullable=False)
    planner_id = db.Column(db.String(100), nullable=False)
    user_id = db.Column(db.String(100), nullable=False)
    airport_code = db.Column(db.String(10), nullable=False)
    passenger_name = db.Column(db.String(100))
    flight_no = db.Column(db.String(20))
    source_location = db.Column(db.String(100))
    departure_date = db.Column(db.String(20))
    departure_time = db.Column(db.String(20))
    arrival_date = db.Column(db.String(20))
    arrival_time = db.Column(db.String(20))
    arrival_location = db.Column(db.String(100))
    airline_name = db.Column(db.String(100))
    ticket_type = db.Column(db.String(20))