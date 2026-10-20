from flask import Blueprint, render_template, request, redirect, url_for, flash
from sqlalchemy import or_

from ..extensions import db, limiter
from ..models import Vehicle, ContactMessage, FinancingApplication
from .forms import ContactForm, FinancingForm

main_bp = Blueprint('main', __name__)

BODY_STYLES = ['Car', 'SUV', 'Truck', 'Commercial']


@main_bp.route('/')
def home():
    featured = (
        Vehicle.query.filter_by(status='available')
        .order_by(Vehicle.created_at.desc())
        .limit(6)
        .all()
    )
    type_counts = {
        style: Vehicle.query.filter_by(body_style=style, status='available').count()
        for style in BODY_STYLES
    }
    makes = [m[0] for m in db.session.query(Vehicle.make).distinct().order_by(Vehicle.make).all()]
    return render_template('index.html', featured=featured, type_counts=type_counts, makes=makes)


@main_bp.route('/inventory')
def inventory():
    query = Vehicle.query

    body_style = request.args.get('body_style', '').strip()
    make = request.args.get('make', '').strip()
    model = request.args.get('model', '').strip()
    keyword = request.args.get('keyword', '').strip()
    min_price = request.args.get('min_price', '').strip()
    max_price = request.args.get('max_price', '').strip()
    sort = request.args.get('sort', 'newest')

    if body_style:
        query = query.filter(Vehicle.body_style == body_style)
    if make:
        query = query.filter(Vehicle.make.ilike(f'%{make}%'))
    if model:
        query = query.filter(Vehicle.model.ilike(f'%{model}%'))
    if keyword:
        like = f'%{keyword}%'
        query = query.filter(
            or_(
                Vehicle.make.ilike(like),
                Vehicle.model.ilike(like),
                Vehicle.trim.ilike(like),
                Vehicle.description.ilike(like),
            )
        )
    if min_price.isdigit():
        query = query.filter(Vehicle.price >= int(min_price))
    if max_price.isdigit():
        query = query.filter(Vehicle.price <= int(max_price))

    if sort == 'price_low':
        query = query.order_by(Vehicle.status.asc(), Vehicle.price.asc())
    elif sort == 'price_high':
        query = query.order_by(Vehicle.status.asc(), Vehicle.price.desc())
    elif sort == 'mileage':
        query = query.order_by(Vehicle.status.asc(), Vehicle.mileage.asc())
    else:
        query = query.order_by(Vehicle.status.asc(), Vehicle.created_at.desc())

    vehicles = query.all()
    makes = [m[0] for m in db.session.query(Vehicle.make).distinct().order_by(Vehicle.make).all()]

    return render_template(
        'inventory.html',
        vehicles=vehicles,
        makes=makes,
        body_styles=BODY_STYLES,
        filters=request.args,
    )


@main_bp.route('/inventory/<int:vehicle_id>')
def vehicle_detail(vehicle_id):
    vehicle = Vehicle.query.get_or_404(vehicle_id)
    return render_template('vehicle_detail.html', vehicle=vehicle)


@main_bp.route('/financing', methods=['GET', 'POST'])
@limiter.limit('10 per hour', methods=['POST'])
def financing():
    form = FinancingForm()
    if form.validate_on_submit():
        entry = FinancingApplication(
            full_name=form.full_name.data,
            email=form.email.data,
            phone=form.phone.data,
            employment_status=form.employment_status.data,
            annual_income=form.annual_income.data,
            down_payment=form.down_payment.data,
            vehicle_interest=form.vehicle_interest.data,
            notes=form.notes.data,
        )
        db.session.add(entry)
        db.session.commit()
        flash('Thanks — your financing request has been sent. A member of our team will follow up shortly.', 'success')
        return redirect(url_for('main.financing'))
    return render_template('financing.html', form=form)


@main_bp.route('/contact', methods=['GET', 'POST'])
@limiter.limit('10 per hour', methods=['POST'])
def contact():
    form = ContactForm()
    if form.validate_on_submit():
        msg = ContactMessage(
            name=form.name.data,
            email=form.email.data,
            phone=form.phone.data,
            subject=form.subject.data,
            message=form.message.data,
        )
        db.session.add(msg)
        db.session.commit()
        flash('Message sent — we will get back to you soon.', 'success')
        return redirect(url_for('main.contact'))
    return render_template('contact.html', form=form)
