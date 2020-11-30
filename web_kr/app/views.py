import datetime

from app import app, db
from app.forms import NewCarForm, EditCarForm
from .models import Car, Condition
from flask import render_template, redirect, url_for, flash, request

@app.route('/', methods=['GET', 'POST'])
def main():
    q = request.args.get('q')
    if q:
        cars = Car.query.filter(Car.license_plate.contains(q) | Car.brand.contains(q))
    else:
        cars = Car.query.order_by(Car.prod_date.desc())
    return render_template('main.html', cars=cars)


@app.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit_car(id):
    available_cond = db.session.query(Condition).all()
    cond_list = [(i.id, i.name) for i in available_cond]
    form = EditCarForm()
    form.condition.choices = cond_list
    car = Car.query.filter_by(id=id).first()
    if form.validate_on_submit():

        car.license_plate = form.license_plate.data
        car.brand = form.brand.data
        car.condition_id = form.condition.data
        car.on_go = form.on_go.data
        car.price = form.price.data
        car.prod_date = form.prod_date.data

        flash("Post edited successfully")
        db.session.commit()
        redirect(url_for('main'))
    elif request.method == 'GET':
        form.license_plate.data = car.license_plate
        form.brand.data = car.brand
        form.condition.data = car.condition
        form.on_go.data = car.on_go
        form.price.data = car.price
    return render_template('edit_car.html', form=form, id=id)


@app.route('/new_car', methods=['GET', 'POST'])
def new_car():
    available_cond = db.session.query(Condition).all()
    form = NewCarForm()
    cond_list = [(i.id, i.name) for i in available_cond]
    form.condition.choices = cond_list
    if form.validate_on_submit():
        l_p = form.license_plate.data
        b = form.brand.data
        c = form.condition.data
        o_g = form.on_go.data
        p = form.price.data
        p_d = form.prod_date.data
        car = Car(license_plate=l_p, brand=b, condition_id=form.condition.data, on_go=o_g, price=p, prod_date=p_d)
        db.session.add(car)
        db.session.commit()
        flash("Car created successfully")
    return render_template('new_car.html', form=form)


@app.route('/delete/<int:id>', methods=["GET", "DELETE"])
def delete_car(id):
    car = Car.query.filter_by(id=id).first()

    db.session.delete(car)
    db.session.commit()
    return redirect(url_for('main'))