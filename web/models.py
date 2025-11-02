from app import db
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
import datetime
import enum

class JobStatus(enum.Enum):
    PENDING = 'PENDING'
    PROCESSING = 'PROCESSING'
    COMPLETE = 'COMPLETE'
    FAILED = 'FAILED'

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(256))
    jobs = db.relationship('Job', backref='user', lazy='dynamic')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Job(db.Model):
    __tablename__ = 'jobs'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    filename = db.Column(db.String(256))
    status = db.Column(db.Enum(JobStatus), default=JobStatus.PENDING, index=True)
    celery_task_id = db.Column(db.String(128))
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow, index=True)
    completed_at = db.Column(db.DateTime)
    error_message = db.Column(db.String(512))
    output_zip_path = db.Column(db.String(512))
