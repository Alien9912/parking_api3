"""API routes."""
from datetime import datetime
from typing import Any, Dict, Tuple

from flask import Blueprint, jsonify, request

from app import db
from app.models import Client, ClientParking, Parking

bp = Blueprint("api", __name__)

@bp.route("/clients", methods=["GET"])
def get_clients() -> Tuple[Any, int]:
    clients = Client.query.all()
    return jsonify([{"id": c.id, "name": c.name, "surname": c.surname,
                     "credit_card": c.credit_card, "car_number": c.car_number} for c in clients]), 200

@bp.route("/clients/<int:client_id>", methods=["GET"])
def get_client(client_id: int) -> Tuple[Any, int]:
    client = Client.query.get_or_404(client_id)
    return jsonify({"id": client.id, "name": client.name, "surname": client.surname,
                    "credit_card": client.credit_card, "car_number": client.car_number}), 200

@bp.route("/clients", methods=["POST"])
def create_client() -> Tuple[Any, int]:
    data: Dict[str, Any] = request.json or {}
    client = Client(name=data["name"], surname=data["surname"],
                    credit_card=data.get("credit_card"), car_number=data.get("car_number"))
    db.session.add(client)
    db.session.commit()
    return jsonify({"id": client.id}), 201

@bp.route("/parkings", methods=["POST"])
def create_parking() -> Tuple[Any, int]:
    data = request.json or {}
    opened = data.get("opened", True)
    count_places = data["count_places"]
    available = count_places if opened else 0
    parking = Parking(address=data["address"], opened=opened, count_places=count_places,
                      count_available_places=available)
    db.session.add(parking)
    db.session.commit()
    return jsonify({"id": parking.id}), 201

@bp.route("/client_parkings", methods=["POST"])
def enter_parking() -> Tuple[Any, int]:
    data = request.json or {}
    client_id, parking_id = data["client_id"], data["parking_id"]
    Client.query.get_or_404(client_id)
    parking = Parking.query.get_or_404(parking_id)
    if not parking.opened:
        return jsonify({"error": "Parking is closed"}), 400
    if parking.count_available_places <= 0:
        return jsonify({"error": "No free places"}), 400
    active = ClientParking.query.filter_by(client_id=client_id, parking_id=parking_id, time_out=None).first()
    if active:
        return jsonify({"error": "Client already on this parking"}), 400
    client_parking = ClientParking(client_id=client_id, parking_id=parking_id, time_in=datetime.utcnow())
    parking.count_available_places -= 1
    db.session.add(client_parking)
    db.session.commit()
    return jsonify({"message": "Entry registered"}), 200

@bp.route("/client_parkings", methods=["DELETE"])
def exit_parking() -> Tuple[Any, int]:
    data = request.json or {}
    client_id, parking_id = data["client_id"], data["parking_id"]
    record = ClientParking.query.filter_by(client_id=client_id, parking_id=parking_id, time_out=None).first()
    if not record:
        return jsonify({"error": "No active entry found"}), 404
    client = Client.query.get(client_id)
    if client is None or not client.credit_card:
        return jsonify({"error": "No credit card linked"}), 400
    parking = Parking.query.get(parking_id)
    record.time_out = datetime.utcnow()
    if parking:
        parking.count_available_places += 1
    db.session.commit()
    return jsonify({"message": "Exit registered and payment processed"}), 200
