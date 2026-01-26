from flask_jwt_extended import get_jwt, verify_jwt_in_request
from flask import jsonify
from functools import wraps

def admin_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        verify_jwt_in_request()

        claims = get_jwt()
        if claims.get("role") != "admin":
            return jsonify({"message": "Admin access required"}), 403

        return fn(*args, **kwargs)
    return wrapper