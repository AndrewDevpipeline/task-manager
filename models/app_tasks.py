from datetime import datetime
from email.policy import default
import marshmallow as ma
from sqlalchemy import ForeignKey
from app import db


class AppTasks(db.Model):
    __tablename__ = "Tasks"
    task_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(ForeignKey("AppUsers.user_id"), nullable=True)
    task_description = db.Column(db.String(), nullable=False)
    status = db.Column(ForeignKey("Swim_lanes.lane_id"))
    task_name = db.Column(db.String(), nullable=False)
    start_date = db.Column(db.dateTime, nullable=True)
    finish_date = db.Column(db.dateTime, nullable=True)
    active = db.Column(db.Boolean(), default=False)
    index = db.Column(db.Integer)

    def __init__(self, task_name, task_description, user_id):
        self.task_name = task_name
        self.task_description = task_description
        self.user_id


class AppUsersSchema(ma.Schema):
    class Meta:
        fields = ['user_id', 'first_name', 'last_name', 'email',
                  'password', 'city', 'state', 'org_id', 'active', 'created_date', 'role', 'organization']


user_schema = AppUsersSchema()
users_schema = AppUsersSchema(many=True)
