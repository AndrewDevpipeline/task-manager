from datetime import datetime
import marshmallow as ma
from app import db


class AppUsers(db.Model):
    __tablename__ = "Users"
    user_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(), nullable=False)
    role = db.Column(db.String(), default='user', nullable=False)
    created_date = db.Column(db.DateTime, default=datetime.utcnow)
    email = db.Column(db.String(), nullable=False, unique=True)
    password = db.Column(db.String(), nullable=False)
    active = db.Column(db.Boolean(), nullable=False, default=False)

    def __init__(self, name, role, email, password):
        self.name = name
        self.role = role
        self.email = email
        self.password = password,
        self.active = True


class AppUsersSchema(ma.Schema):
    class Meta:
        fields = ['user_id', 'name', 'role',
                  'created_date', 'email', 'password', 'active']


user_schema = AppUsersSchema()
users_schema = AppUsersSchema(many=True)
