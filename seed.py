"""Creates the database tables, a demo dealer login, and a handful of
sample vehicles so the site isn't empty on first run.

Usage:
    python seed.py
"""
from vowapp import create_app
from vowapp.extensions import db
from vowapp.models import Dealer, Vehicle

DEMO_EMAIL = 'dealer@vowmotors.com'
DEMO_PASSWORD = 'ChangeMe123!'

app = create_app()

with app.app_context():
    db.create_all()

    dealer = Dealer.query.filter_by(email=DEMO_EMAIL).first()
    if not dealer:
        dealer = Dealer(name='Vow Motors Staff', email=DEMO_EMAIL)
        dealer.set_password(DEMO_PASSWORD)
        db.session.add(dealer)
        db.session.commit()
        print(f'Created demo dealer login: {DEMO_EMAIL} / {DEMO_PASSWORD}')
    else:
        print(f'Demo dealer already exists: {DEMO_EMAIL}')

    if Vehicle.query.count() == 0:
        sample = [
            dict(year=2022, make='Honda', model='Civic', trim='EX', body_style='Car',
                 price=21500, mileage=29773, exterior_color='Silver', transmission='CVT',
                 fuel_type='Gasoline', status='available',
                 description='One owner, clean history, recently serviced.'),
            dict(year=2021, make='Ford', model='F-150', trim='XLT', body_style='Truck',
                 price=34900, mileage=43452, exterior_color='Black', transmission='Automatic',
                 fuel_type='Gasoline', status='available',
                 description='Crew cab, tow package, bed liner included.'),
            dict(year=2023, make='Toyota', model='RAV4', trim='LE', body_style='SUV',
                 price=27800, mileage=15772, exterior_color='Blue', transmission='Automatic',
                 fuel_type='Hybrid', status='available',
                 description='Hybrid AWD, still under factory warranty.'),
            dict(year=2020, make='Chevrolet', model='Express 2500', trim='Cargo', body_style='Commercial',
                 price=25900, mileage=66305, exterior_color='White', transmission='Automatic',
                 fuel_type='Gasoline', status='sold',
                 description='Fleet-maintained cargo van, shelving included.'),
        ]
        for data in sample:
            db.session.add(Vehicle(dealer_id=dealer.id, **data))
        db.session.commit()
        print(f'Seeded {len(sample)} sample vehicles.')
    else:
        print('Vehicles already exist — skipped sample inventory.')

    print('Done.')
