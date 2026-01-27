from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from backend.models import Placement, db, Company, JobPosition, Application, Student
from backend.routes.utils import company_required
from datetime import date

company_bp = Blueprint("company", __name__)

@company_bp.route("/dashboard", methods=["GET"])
@jwt_required()
@company_required
def company_dashboard():
    user_id = int(get_jwt_identity())

    company = Company.query.filter_by(user_id=user_id).first()
    if not company or company.approval_status != "Approved":
        return jsonify({"message": "Company not approved"}), 403

    jobs = JobPosition.query.filter_by(company_id=company.id).count()
    applications = Application.query.join(JobPosition).filter(
        JobPosition.company_id == company.id
    ).count()

    return jsonify({
        "company": company.name,
        "total_jobs": jobs,
        "total_applications": applications
    })


@company_bp.route("/jobs", methods=["POST"])
@jwt_required()
@company_required
def create_job():
    user_id = int(get_jwt_identity())
    company = Company.query.filter_by(user_id=user_id).first()

    if company.approval_status != "Approved":
        return jsonify({"message": "Company not approved"}), 403

    data = request.json

    job = JobPosition(
        company_id=company.id,
        title=data["title"],
        description=data.get("description"),
        salary=data.get("salary"),
        skills_required=data.get("skills_required"),
        status="Pending"
    )

    db.session.add(job)
    db.session.commit()

    return jsonify({"message": "Job created and awaiting admin approval"}), 201


@company_bp.route("/jobs", methods=["GET"])
@jwt_required()
@company_required
def get_company_jobs():
    user_id = int(get_jwt_identity())
    company = Company.query.filter_by(user_id=user_id).first()

    jobs = JobPosition.query.filter_by(company_id=company.id).all()

    return jsonify([
        {
            "id": j.id,
            "title": j.title,
            "status": j.status
        }
        for j in jobs
    ])


@company_bp.route("/jobs/<int:job_id>/applications", methods=["GET"])
@jwt_required()
@company_required
def view_applications(job_id):
    user_id = int(get_jwt_identity())
    company = Company.query.filter_by(user_id=user_id).first()

    job = JobPosition.query.get_or_404(job_id)
    if job.company_id != company.id:
        return jsonify({"message": "Unauthorized access"}), 403

    applications = Application.query.filter_by(job_id=job_id).all()

    return jsonify([
        {
            "application_id": a.id,
            "student_id": a.student_id,
            "status": a.status
        }
        for a in applications
    ])


@company_bp.route("/applications/<int:application_id>/status", methods=["PUT"])
@jwt_required()
@company_required
def update_application_status(application_id):
    user_id = int(get_jwt_identity())
    company = Company.query.filter_by(user_id=user_id).first()

    application = Application.query.get_or_404(application_id)
    job = JobPosition.query.get(application.job_id)

    if job.company_id != company.id:
        return jsonify({"message": "Unauthorized"}), 403

    data = request.json
    ALLOWED_TRANSITIONS = {
        "Applied": ["Shortlisted", "Rejected"],
        "Shortlisted": ["Interview", "Rejected"],
        "Interview": ["Selected", "Rejected"],
        "Selected": [],
        "Rejected": []
    }

    new_status = data.get("status")
    
    if application.status is None:
        application.status = "Applied"
 
    if new_status not in ALLOWED_TRANSITIONS.get(application.status, []):
        return jsonify({"message": "Invalid status transition"}), 400

    application.status = new_status

    if new_status == "Selected":
        placement = Placement(
            application_id=application.id,
            company_id=job.company_id,
            student_id=application.student_id,
            position=job.title,
            salary=job.salary,
            joining_date=date.today()
        )
        db.session.add(placement)

    db.session.commit()
    return jsonify({"message": "Application status updated"})


