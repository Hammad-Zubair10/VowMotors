import os

from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app, abort
from flask_login import login_user, logout_user, login_required, current_user

from ..extensions import db, limiter
from ..models import Dealer, Vehicle, VehiclePhoto, ContactMessage, FinancingApplication
from ..utils import save_photo, send_reset_email
from .forms import ChangePasswordForm, LoginForm, RequestResetForm, ResetPasswordForm, VehicleForm

dealer_bp = Blueprint('dealer', __name__)

@dealer_bp.route('/login', methods=['GET', 'POST'])
@limiter.limit('5 per minute;30 per hour', methods=['POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dealer.dashboard'))
    form = LoginForm()
    if form.validate_on_submit():
        dealer = Dealer.query.filter_by(email=form.email.data.lower().strip()).first()
        if dealer and dealer.check_password(form.password.data):
            login_user(dealer)
            next_url = request.args.get('next')
            return redirect(next_url or url_for('dealer.dashboard'))
        flash('Invalid email or password.', 'error')
    return render_template('dealer/login.html', form=form)

@dealer_bp.route('/reset_password', methods=['GET', 'POST'])
@limiter.limit('5 per hour', methods=['POST'])
def reset_request():
    if current_user.is_authenticated:
        return redirect(url_for('dealer.dashboard'))
    form = RequestResetForm()
    if form.validate_on_submit():
        dealer = Dealer.query.filter_by(email=form.email.data.lower().strip()).first()
        if dealer:
            try:
                send_reset_email(dealer)
            except Exception:
                current_app.logger.exception('Failed to send password reset email')
                flash('Could not send the reset email right now. Please try again later.', 'error')
                return render_template('dealer/reset_request.html', form=form)
        flash('If that email is registered, a reset link has been sent.', 'success')
        return redirect(url_for('dealer.login'))
    return render_template('dealer/reset_request.html', form=form)


@dealer_bp.route('/reset_password/<token>', methods=['GET', 'POST'])
@limiter.limit('10 per hour', methods=['POST'])
def reset_password(token):
    if current_user.is_authenticated:
        return redirect(url_for('dealer.dashboard'))
    dealer = Dealer.verify_reset_token(token, max_age=current_app.config['PASSWORD_RESET_MAX_AGE'])
    if dealer is None:
        flash('That reset link is invalid or has expired.', 'error')
        return redirect(url_for('dealer.reset_request'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        dealer.set_password(form.new_password.data)
        db.session.commit()
        flash('Your password has been updated. You can log in now.', 'success')
        return redirect(url_for('dealer.login'))
    return render_template('dealer/reset_password.html', form=form)


@dealer_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'success')
    return redirect(url_for('main.home'))


@dealer_bp.route('/')
@login_required
def dashboard():
    vehicles = Vehicle.query.order_by(Vehicle.created_at.desc()).all()
    stats = {
        'total': len(vehicles),
        'available': sum(1 for v in vehicles if v.status == 'available'),
        'sold': sum(1 for v in vehicles if v.status == 'sold'),
    }
    return render_template('dealer/dashboard.html', vehicles=vehicles, stats=stats)


def _apply_form(form, vehicle):
    vehicle.year = form.year.data
    vehicle.make = form.make.data.strip()
    vehicle.model = form.model.data.strip()
    vehicle.trim = form.trim.data
    vehicle.body_style = form.body_style.data
    vehicle.price = form.price.data
    vehicle.mileage = form.mileage.data or 0
    vehicle.exterior_color = form.exterior_color.data
    vehicle.transmission = form.transmission.data
    vehicle.fuel_type = form.fuel_type.data
    vehicle.vin = form.vin.data or None
    vehicle.status = form.status.data
    vehicle.description = form.description.data


def _save_uploaded_photos(vehicle):
    files = [f for f in request.files.getlist('photos') if f and f.filename]
    position = vehicle.photos.count()
    max_photos = current_app.config['MAX_PHOTOS_PER_VEHICLE']
    available = max(0, max_photos - position)

    if len(files) > available:
        skipped = len(files) - available
        files = files[:available]
        if skipped > 0:
            flash(
                f'This vehicle allows a maximum of {max_photos} photos. '
                f'{skipped} photo(s) were not uploaded.',
                'error',
            )

    for f in files:
        filename = save_photo(f)
        db.session.add(VehiclePhoto(vehicle_id=vehicle.id, filename=filename, position=position))
        position += 1


@dealer_bp.route('/vehicles/new', methods=['GET', 'POST'])
@login_required
def vehicle_new():
    form = VehicleForm()
    if form.validate_on_submit():
        vehicle = Vehicle(dealer_id=current_user.id)
        _apply_form(form, vehicle)
        db.session.add(vehicle)
        db.session.flush()  # assign vehicle.id before saving photos
        _save_uploaded_photos(vehicle)
        db.session.commit()
        flash('Vehicle added to inventory.', 'success')
        return redirect(url_for('dealer.dashboard'))
    return render_template('dealer/vehicle_form.html', form=form, vehicle=None)


@dealer_bp.route('/vehicles/<int:vehicle_id>/edit', methods=['GET', 'POST'])
@login_required
def vehicle_edit(vehicle_id):
    vehicle = Vehicle.query.get_or_404(vehicle_id)
    form = VehicleForm(obj=vehicle)
    if form.validate_on_submit():
        _apply_form(form, vehicle)
        _save_uploaded_photos(vehicle)
        db.session.commit()
        flash('Vehicle updated.', 'success')
        return redirect(url_for('dealer.dashboard'))
    return render_template('dealer/vehicle_form.html', form=form, vehicle=vehicle)


@dealer_bp.route('/vehicles/<int:vehicle_id>/delete', methods=['POST'])
@login_required
def vehicle_delete(vehicle_id):
    vehicle = Vehicle.query.get_or_404(vehicle_id)
    for photo in vehicle.photos:
        path = os.path.join(current_app.config['UPLOAD_FOLDER'], photo.filename)
        if os.path.exists(path):
            os.remove(path)
    db.session.delete(vehicle)
    db.session.commit()
    flash('Vehicle removed.', 'success')
    return redirect(url_for('dealer.dashboard'))


@dealer_bp.route('/vehicles/<int:vehicle_id>/photos/<int:photo_id>/delete', methods=['POST'])
@login_required
def photo_delete(vehicle_id, photo_id):
    photo = VehiclePhoto.query.get_or_404(photo_id)
    if photo.vehicle_id != vehicle_id:
        abort(404)
    path = os.path.join(current_app.config['UPLOAD_FOLDER'], photo.filename)
    if os.path.exists(path):
        os.remove(path)
    db.session.delete(photo)
    db.session.commit()
    flash('Photo removed.', 'success')
    return redirect(url_for('dealer.vehicle_edit', vehicle_id=vehicle_id))


@dealer_bp.route('/account/password', methods=['GET', 'POST'])
@login_required
@limiter.limit('10 per hour', methods=['POST'])
def change_password():
    form = ChangePasswordForm()
    if form.validate_on_submit():
        if not current_user.check_password(form.current_password.data):
            flash('Current password is incorrect.', 'error')
        else:
            current_user.set_password(form.new_password.data)
            db.session.commit()
            flash('Password updated.', 'success')
            return redirect(url_for('dealer.dashboard'))
    return render_template('dealer/change_password.html', form=form)


@dealer_bp.route('/messages')
@login_required
def messages():
    contacts = ContactMessage.query.order_by(ContactMessage.created_at.desc()).all()
    financing_apps = FinancingApplication.query.order_by(FinancingApplication.created_at.desc()).all()
    return render_template('dealer/messages.html', contacts=contacts, financing_apps=financing_apps)
