from datetime import datetime

from flask import request, jsonify

from app import app, db
from .models import Car


@app.route('/cars/<int:car_id>', methods=['GET'])
@app.route('/cars', methods=['GET'])
def get_cars(car_id=None):
    if car_id:
        car = Car.query.filter_by(id=car_id).first()
        if not car:
            return jsonify({"details": "Not found"})
        result = {'id': car.id,
                  'license_plate': car.license_plate,
                  'brand': car.brand,
                  'condition_id': car.condition_id,
                  'on_go': car.on_go,
                  'price': car.price,
                  'prod_date': car.prod_date
                  }
        return jsonify(result)
    else:
        cars = Car.query.all()
        result = []
        for car in cars:
            result.append({'id': car.id,
                           'license_plate': car.license_plate,
                           'brand': car.brand,
                           'condition_id': car.condition_id,
                           'on_go': car.on_go,
                           'price': car.price,
                           'prod_date': car.prod_date
                           })
        return jsonify(result)


@app.route('/cars/<int:car_id>', methods=['PUT'])
def edit_car(car_id):
    car = Car.query.filter_by(id=car_id).first()
    if not car:
        return jsonify({'details': 'Not found'})
    post_data = request.json
    car.license_plate = post_data['license_plate']
    car.brand = post_data['brand']
    car.condition_id = post_data['condition_id']
    car.on_go = post_data['on_go']
    car.price = post_data['price']
    car.prod_date = datetime.utcnow()
    db.session.commit()
    return jsonify({'details': 'Success'})


@app.route('/cars', methods=['POST'])
def create_car():
    post_data = request.json
    car = Car(license_plate=post_data['license_plate'], brand=post_data['brand'],
              condition_id=post_data['condition_id'], on_go=post_data['on_go'], price=post_data['price'],
              prod_date=datetime.utcnow())
    db.session.add(car)
    db.session.commit()
    return jsonify({'details': 'Success'})


@app.route('/cars/<int:car_id>', methods=["GET", "DELETE"])
def delete_car(car_id):
    car = Car.query.filter_by(id=car_id).first()
    if not car:
        return jsonify({'detail': 'Not found'})
    else:
        db.session.delete(car)
        db.session.commit()
        return jsonify({'details': 'Success'})
