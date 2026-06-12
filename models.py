from sqlalchemy import ForeignKey
from ext import db, login_manager
from flask_login import UserMixin
from datetime import datetime


class BaseModel:
    def create(self):
        db.session.add(self)
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    @staticmethod
    def save():
        db.session.commit()


class User(db.Model, BaseModel, UserMixin):
    __tablename__ = "users"

    id = db.Column(db.Integer(), primary_key=True)
    username = db.Column(db.String())
    password = db.Column(db.String())
    role = db.Column(db.String(), default="Guest")


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)


class Job(db.Model, BaseModel):
    __tablename__ = "jobs"

    id = db.Column(db.Integer(), primary_key=True)
    title = db.Column(db.String(), nullable=False)
    category = db.Column(db.String(), nullable=False)
    salary = db.Column(db.String())
    is_remote = db.Column(db.Boolean(), default=False)
    danger_level = db.Column(db.String(), default="Low")
    img = db.Column(db.String(), default="default.jpg")
    description = db.Column(db.Text())


class Review(db.Model, BaseModel):
    __tablename__ = "reviews"

    id = db.Column(db.Integer(), primary_key=True)
    text = db.Column(db.String(), nullable=False)
    job_id = db.Column(ForeignKey("jobs.id"))

class UniquenessRequest(db.Model, BaseModel):
    __tablename__ = "uniqueness_requests"


    id = db.Column(db.Integer(), primary_key=True)
    user_id = db.Column(ForeignKey("users.id"))


    title = db.Column(db.String(), nullable=False)
    category = db.Column(db.String(), nullable=False)
    salary = db.Column(db.String())
    danger_level = db.Column(db.String(), default="Low")
    img = db.Column(db.String(), default="default.jpg")
    description = db.Column(db.Text())


    message_to_admin = db.Column(db.Text())
    status = db.Column(db.String(), default="pending")  # pending | approved | rejected
    created_at = db.Column(db.DateTime(), default=datetime.utcnow)

    user = db.relationship("User", backref="uniqueness_requests")