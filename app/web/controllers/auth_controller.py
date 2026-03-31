from flask import Blueprint, request, jsonify
from app.web.services.auth_service import login_user, register_user

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.json
    result = login_user(
        data["email"],
        data["password"]
    )
    return jsonify(result)