import pytest

from app.models import Client, ClientParking, Parking


def test_get_clients(client, sample_data):
    response = client.get("/clients")
    assert response.status_code == 200
    assert len(response.json) == 1


def test_get_client_by_id(client, sample_data):
    client_id = sample_data["client"].id
    response = client.get(f"/clients/{client_id}")
    assert response.status_code == 200
    assert response.json["name"] == "John"


@pytest.mark.parametrize("endpoint", ["/clients", "/clients/1"])
def test_get_endpoints_status(client, endpoint, sample_data):
    if endpoint == "/clients/1":
        endpoint = f"/clients/{sample_data['client'].id}"
    response = client.get(endpoint)
    assert response.status_code == 200


def test_create_client(client, db):
    data = {
        "name": "Jane",
        "surname": "Smith",
        "credit_card": "9876543210",
        "car_number": "XYZ789",
    }
    response = client.post("/clients", json=data)
    assert response.status_code == 201
    assert Client.query.count() == 1


def test_create_parking(client, db):
    data = {"address": "New Parking", "opened": True, "count_places": 20}
    response = client.post("/parkings", json=data)
    assert response.status_code == 201
    parking = Parking.query.first()
    assert parking.count_available_places == 20


@pytest.mark.parking
def test_enter_parking(client, sample_data, db):
    client_id = sample_data["client"].id
    parking_id = sample_data["parking"].id
    db.session.delete(sample_data["entry"])
    db.session.commit()
    initial = Parking.query.get(parking_id).count_available_places
    response = client.post(
        "/client_parkings", json={"client_id": client_id, "parking_id": parking_id}
    )
    assert response.status_code == 200
    new_available = Parking.query.get(parking_id).count_available_places
    assert new_available == initial - 1


@pytest.mark.parking
def test_exit_parking(client, sample_data):
    client_id = sample_data["client"].id
    parking_id = sample_data["parking"].id
    initial = Parking.query.get(parking_id).count_available_places
    response = client.delete(
        "/client_parkings", json={"client_id": client_id, "parking_id": parking_id}
    )
    assert response.status_code == 200
    new_available = Parking.query.get(parking_id).count_available_places
    assert new_available == initial + 1


def test_exit_without_card(client, sample_data, db):
    client_obj = sample_data["client"]
    client_obj.credit_card = None
    db.session.commit()
    response = client.delete(
        "/client_parkings",
        json={"client_id": client_obj.id, "parking_id": sample_data["parking"].id},
    )
    assert response.status_code == 400
    assert "No credit card" in response.json["error"]
