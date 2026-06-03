from datetime import datetime, timedelta
import pytest
from app import create_app, db as _db
from app.models import Client, ClientParking, Parking


@pytest.fixture
def app():
    app = create_app(
        {"TESTING": True, "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:"}
    )
    with app.app_context():
        _db.create_all()
        yield app
        _db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def db(app):
    with app.app_context():
        yield _db


@pytest.fixture
def sample_data(db):
    client = Client(
        name="John",
        surname="Doe",
        credit_card="1234567890123456",
        car_number="ABC123",
    )
    parking = Parking(
        address="Test str, 1",
        opened=True,
        count_places=10,
        count_available_places=5,
    )
    db.session.add_all([client, parking])
    db.session.commit()
    entry = ClientParking(
        client_id=client.id,
        parking_id=parking.id,
        time_in=datetime.utcnow() - timedelta(hours=1),
    )
    db.session.add(entry)
    db.session.commit()
    return {"client": client, "parking": parking, "entry": entry}
