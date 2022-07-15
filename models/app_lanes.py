from db import db
import marshmallow as ma


class AppLanes(db.Model):
    __tablename__ = "Lanes"
    lane_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(), nullable=False, unique=True)
    order = db.Column(db.Integer, nullable=False, autoincrement=True)

    def __init__(self, name, order):
        self.name = name
        self.order = order


class AppLanesSchema(ma.Schema):
    class Meta:
        fields = ['lane_id', 'name', 'order']


lane_schema = AppLanesSchema()
lanes_schema = AppLanesSchema(many=True)
