# models.py
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class TrafficImage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    image_path = db.Column(db.String, nullable=False)
    timestamp = db.Column(db.DateTime, nullable=False)
    congested = db.Column(db.Boolean, nullable=False)

    def __repr__(self):
        return f'<TrafficImage {self.id}>'
