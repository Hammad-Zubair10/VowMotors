import os
import uuid

from flask import current_app, url_for
from flask_mail import Message
from werkzeug.utils import secure_filename

from .extensions import mail


def allowed_file(filename):
    return (
        '.' in filename
        and filename.rsplit('.', 1)[1].lower() in current_app.config['ALLOWED_EXTENSIONS']
    )


def save_photo(file_storage):
    """Save an uploaded FileStorage under a random name and return the filename."""
    original = secure_filename(file_storage.filename)
    ext = original.rsplit('.', 1)[1].lower() if '.' in original else 'jpg'
    filename = f"{uuid.uuid4().hex}.{ext}"
    os.makedirs(current_app.config['UPLOAD_FOLDER'], exist_ok=True)
    file_storage.save(os.path.join(current_app.config['UPLOAD_FOLDER'], filename))
    return filename


def send_reset_email(dealer):
    token = dealer.get_reset_token()
    reset_url = url_for('dealer.reset_password', token=token, _external=True)
    msg = Message(
        subject=f"Password reset · {current_app.config['DEALERSHIP_NAME']}",
        recipients=[dealer.email],
        body=(
            f"Hi {dealer.name},\n\n"
            "Someone requested a password reset for your dealer portal account. "
            f"Click the link below to choose a new password (valid for 1 hour):\n\n{reset_url}\n\n"
            "If you didn't request this, you can safely ignore this email."
        ),
    )
    mail.send(msg)
