"""Creates (or updates the password for) a dealer login.

Usage:
    python create_dealer.py
"""
import getpass

from vowapp import create_app
from vowapp.extensions import db
from vowapp.models import Dealer

app = create_app()

with app.app_context():
    db.create_all()

    name = input('Dealer name: ').strip()
    email = input('Login email: ').strip().lower()
    password = getpass.getpass('Password (min 8 characters): ')
    confirm = getpass.getpass('Confirm password: ')

    if password != confirm:
        print('Passwords do not match. Nothing was changed.')
    elif len(password) < 8:
        print('Password must be at least 8 characters. Nothing was changed.')
    else:
        dealer = Dealer.query.filter_by(email=email).first()
        if dealer:
            dealer.set_password(password)
            db.session.commit()
            print(f'Updated password for existing login: {email}')
        else:
            dealer = Dealer(name=name or 'Dealer', email=email)
            dealer.set_password(password)
            db.session.add(dealer)
            db.session.commit()
            print(f'Created new dealer login: {email}')
