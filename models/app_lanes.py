import marshmallow as ma
from app import db


class AppLanes(db.Model):
    __tablename__ = "Lanes"
    lane_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(), nullable=False)
    order = db.Column(db.Integer, nullable=False, autoincrement=True)

    def __init__(self, name):
        self.name = name


class AppLanesSchema(ma.Schema):
    class Meta:
        fields = ['lane_id', 'name', 'order']


lanes_schema = AppLanesSchema()
lanes_schema = AppLanesSchema(many=True)
