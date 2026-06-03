import random
from app.models import Client, Parking
from factory import Faker, LazyAttribute
from factory.alchemy import SQLAlchemyModelFactory
from app import db

class ClientFactory(SQLAlchemyModelFactory):
    class Meta:
        model = Client
        sqlalchemy_session = db.session
    name = Faker("first_name")
    surname = Faker("last_name")
    credit_card = Faker("credit_card_number")
    car_number = Faker("license_plate")
    @classmethod
    def _create(cls, model_class, *args, **kwargs):
        if random.random() < 0.3:
            kwargs["credit_card"] = None
        return super()._create(model_class, *args, **kwargs)

class ParkingFactory(SQLAlchemyModelFactory):
    class Meta:
        model = Parking
        sqlalchemy_session = db.session
    address = Faker("street_address")
    opened = Faker("boolean")
    count_places = Faker("random_int", min=1, max=100)
    count_available_places = LazyAttribute(lambda o: o.count_places if o.opened else 0)

def test_create_client_with_factory(client, db):
    fake_client = ClientFactory.build()
    data = {"name": fake_client.name, "surname": fake_client.surname,
            "credit_card": fake_client.credit_card, "car_number": fake_client.car_number}
    response = client.post("/clients", json=data)
    assert response.status_code == 201
    saved = Client.query.get(response.json["id"])
    assert saved.name == data["name"]

def test_create_parking_with_factory(client, db):
    fake_parking = ParkingFactory.build()
    data = {"address": fake_parking.address, "opened": fake_parking.opened, "count_places": fake_parking.count_places}
    response = client.post("/parkings", json=data)
    assert response.status_code == 201
    saved = Parking.query.get(response.json["id"])
    assert saved.address == data["address"]
