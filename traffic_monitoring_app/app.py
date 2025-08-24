# app.py
from flask import Flask, request, jsonify
from models import db, TrafficImage
from datetime import datetime
import os

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///traffic_images.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

@app.before_first_request
def create_tables():
    db.create_all()

@app.route('/upload', methods=['POST'])
def upload_image():
    data = request.json
    image_path = data['image_path']
    congested = data['congested']
    timestamp = datetime.now()

    new_image = TrafficImage(image_path=image_path, congested=congested, timestamp=timestamp)
    db.session.add(new_image)
    db.session.commit()
    
    return jsonify({'message': 'Image uploaded successfully'}), 201

@app.route('/traffic_analysis', methods=['GET'])
def traffic_analysis():
    results = db.session.query(TrafficImage).all()
    return jsonify([{'id': img.id, 'image_path': img.image_path, 'timestamp': img.timestamp, 'congested': img.congested} for img in results])

if __name__ == '__main__':
    app.run(debug=True)
