from db import db
from sqlalchemy import ForeignKey
from datetime import datetime
import marshmallow as ma


class AppTasks(db.Model):
    __tablename__ = "Tasks"
    task_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(ForeignKey("Users.user_id"), nullable=True)
    task_name = db.Column(db.String(), nullable=True)
    task_description = db.Column(db.String(), nullable=True)
    status = db.Column(ForeignKey("Lanes.lane_id"),
                       default="backlog", nullable=False)
    start_date = db.Column(db.DateTime, nullable=True)
    finish_date = db.Column(db.DateTime, nullable=True)
    active = db.Column(db.Boolean(), default=False, nullable=False)
    index = db.Column(db.Integer, nullable=False)

    def __init__(self, user_id, task_name, task_description, status,  index):
        self.user_id = user_id
        self.task_name = task_name
        self.task_description = task_description
        self.status = status
        self.index = index


class AppTasksSchema(ma.Schema):
    class Meta:
        fields = ['task_id', 'user_id', 'task_name', 'task_description',
                  'status', 'start_date', 'finish_date', 'active', 'index']


task_schema = AppTasksSchema()
tasks_schema = AppTasksSchema(many=True)
