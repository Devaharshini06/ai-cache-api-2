from flask import Blueprint, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import create_access_token
from backend.models import db, User, Student, Company

auth_bp = Blueprint("auth", __name__)

@auth_bp.route("/register/student", methods=["POST"])
def register_student():
    data = request.json

    if User.query.filter_by(email=data["email"]).first():
        return jsonify({"message": "Email already registered"}), 400

    user = User(
        email=data["email"],
        password=generate_password_hash(data["password"]),
        role="student"
    )
    db.session.add(user)
    db.session.commit()

    student = Student(
        user_id=user.id,
        education=data.get("education"),
        skills=data.get("skills"),
        cgpa=data.get("cgpa")
    )
    db.session.add(student)
    db.session.commit()

    return jsonify({"message": "Student registered successfully"}), 201

@auth_bp.route("/register/company", methods=["POST"])
def register_company():
    data = request.json

    if User.query.filter_by(email=data["email"]).first():
        return jsonify({"message": "Email already registered"}), 400

    user = User(
        email=data["email"],
        password=generate_password_hash(data["password"]),
        role="company"
    )
    db.session.add(user)
    db.session.commit()

    company = Company(
        user_id=user.id,
        name=data.get("name"),
        industry=data.get("industry"),
        location=data.get("location")
    )
    db.session.add(company)
    db.session.commit()

    return jsonify({"message": "Company registered. Await admin approval."}), 201

@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.json
    user = User.query.filter_by(email=data["email"]).first()

    if not user or not check_password_hash(user.password, data["password"]):
        return jsonify({"message": "Invalid credentials"}), 401

    if not user.is_active:
        return jsonify({"message": "Account deactivated"}), 403

    access_token = create_access_token(
        identity=str(user.id),              # MUST be string
        additional_claims={"role": user.role}
    )

    return jsonify({
        "access_token": access_token,
        "role": user.role
    })

