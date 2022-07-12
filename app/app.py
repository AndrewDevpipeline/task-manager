# TODO:
# 1. if any tasks reference a lane we try and delete it will error out.
# 2. go through error handling for each endpoint.

from enum import unique
from flask import request, Flask, jsonify, Response
from flask_marshmallow import Marshmallow
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import ForeignKey
from datetime import datetime
import marshmallow as ma

app = Flask(__name__)

database_host = "127.0.0.1:5432"
database_name = "task_manager"
app.config['SQLALCHEMY_DATABASE_URI'] = 'DATBASE_URL'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
ma = Marshmallow(app)


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


lanes_schema = AppLanesSchema()
lanes_schema = AppLanesSchema(many=True)


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


tasks_schema = AppTasksSchema()
tasks_schema = AppTasksSchema(many=True)


def create_all():
    db.create_all()
    print('Querying for Tony Stark...')
    admin_data = db.session.query(AppUsers).filter(
        AppUsers.email == "tony@gmail.com").first()

    if admin_data == None:
        print("Tony Stark not found! Creating tony@gmail.com user...")
        password = ''
        while password == '' or password is None:
            password = input(' Enter a password for Super Admin:')

        record = AppUsers('Tony Stark', 'super-admin',
                          'tony@gmail.com', password)

        db.session.add(record)
        db.session.commit()
        print("Tony Stark Created")
    else:
        print("Tony already exists!")

    print("Querying for backlog...")
    lane_data = db.session.query(AppLanes).filter(
        AppLanes.name == "backlog").first()

    if lane_data == None:
        print("backlog does not exist. creating...")
        record = AppLanes("backlog", 1)
        db.session.add(record)
        db.session.commit()


@app.route("/task/add", methods=["POST"])
def add_task():
    json_data = request.json
    try:
        new_task = AppTasks(
            user_id=json_data["user_id"],
            task_name=json_data["task_name"],
            task_description=json_data["task_description"],
            status=json_data["status"],
            index=json_data["index"])
    except:
        return "missing fields", 400

    db.session.add(new_task)
    db.session.commit()
    return "task added!", 200


@app.route("/")
def home_view():
    return "<h1>Welcome to Andrew's task manager</h1>"


@app.route("/task/edit", methods=["POST"])
def update_task():
    data = request.json
    task_record = db.session.query(AppTasks).filter(
        AppTasks.task_id == data["task_id"]).first()
    if not task_record:
        return "task not found...", 400

    if data["user_id"]:
        task_record.user_id = data["user_id"]
    if data["task_name"]:
        task_record.task_name = data["task_name"]
    if data["task_description"]:
        task_record.task_description = data["task_description"]
    if data["status"]:
        task_record.status = data["status"]
    if data["index"]:
        task_record.index = data["index"]

    db.session.commit()

    return "task updated successfully", 200


@app.route("/task/list", methods=["GET"])
def get_tasks():
    tasks = db.session.query(AppTasks).all()
    return jsonify(tasks_schema.dump(tasks)), 200


@app.route("/task/deactivate", methods=["POST"])
def deactivate_task():
    data = request.json
    task_record = db.session.query(AppTasks).filter(
        AppTasks.task_id == data["task_id"]).first()
    if task_record == None:
        return "task does'nt exist", 400

    task_record.active = False
    db.session.commit()
    return "task deactivated", 200


@app.route("/task/activate", methods=["POST"])
def activate_task():
    data = request.json
    task_record = db.session.query(AppTasks).filter(
        AppTasks.task_id == data["task_id"]).first()
    if task_record == None:
        return "task does'nt exist", 400

    task_record.active = True
    db.session.commit()
    return "task activated", 200


@app.route("/lane/add", methods=["POST"])
def add_lane():
    data = request.json
    try:
        new_lane = AppLanes(
            name=data["name"],
            order=data["order"]
        )
    except:
        return "missing fields", 400

    db.session.add(new_lane)
    db.session.commit()
    return "Lane added successfully", 200


@app.route("/lane/edit", methods=["POST"])
def edit_lane():
    data = request.json
    lane_record = db.session.query(AppLanes).filter(
        AppLanes.lane_id == data["lane_id"]).first()

    if lane_record == None:
        return "lane does'nt exist", 400

    lane_record.name = data["name"]
    lane_record.order = data["order"]
    db.session.commit()
    return "lane updated successfully", 200


@app.route("/lane/list", methods=["GET"])
def lane_list():
    lanes = db.session.query(AppLanes).all()
    return jsonify(lanes_schema.dump(lanes)), 200


# @app.route("/lane/deactivate", methods=["POST"])
# def lane_deactivate():
#     data = request.json
#     lane_record = db.session.query(AppLanes).filter(
#         AppLanes.lane_id == data["lane_id"]).first()

#     if lane_record == None:
#         return "lane doesnt exist", 400

#     lane_record.active = False
#     db.session.commit()
#     return "lane deactivated", 200


# @app.route("/lane/activate", methods=["POST"])
# def lane_activate():
    # data = request.json
    # lane_record = db.session.query(AppLanes).filter(
    #     AppLanes.lane_id == data["lane_id"]).first()

    # if lane_record == None:
    #     return "lane doesnt exist", 400

    # lane_record.active = True
    # db.session.commit()
    # return "lane activated", 200

@app.route("/lane/delete", methods=["DELETE"])
def lane_delete():
    data = request.json

    lane_record = db.session.query(AppLanes).filter(
        AppLanes.lane_id == data["lane_id"]).first()

    if lane_record == None:
        return "lane does not exist", 400

    db.session.query(AppLanes).filter(
        AppLanes.lane_id == data["lane_id"]).delete()
    db.session.commit()

    return "lane has been deleted", 200


@app.route("/add/user", methods=["POST"])
def add_user():
    data = request.json

    try:
        new_user = AppUsers(
            name=data["name"],
            role=data["role"],
            email=data["email"],
            password=data["password"]
        )
    except:
        return "error adding new user", 400

    db.session.add(new_user)
    db.session.commit()
    return "user added successfully", 200


@app.route("/edit/user", methods=["POST"])
def edit_user():
    data = request.json
    user_record = db.session.query(AppUsers).filter(
        AppUsers.user_id == data["user_id"]).first()

    if user_record == None:
        return "user does'nt exist", 400

    if data["name"]:
        user_record.name = data["name"]
    if data["role"]:
        user_record.role = data["role"]
    if data["email"]:
        user_record.email = data["email"]
    if data["password"]:
        user_record.password = data["password"]

    db.session.commit()
    return "user updated successfully", 200


@app.route("/user/list", methods=["GET"])
def user_list():
    users = db.session.query(AppUsers).all()
    return jsonify(users_schema.dump(users)), 200


@app.route("/user/deactivate", methods=["POST"])
def user_deactivate():
    data = request.json
    user_record = db.session.query(AppUsers).filter(
        AppUsers.user_id == data["user_id"]).first()

    if user_record == None:
        return "user doesnt exist", 400

    user_record.active = False
    db.session.commit()
    return "user deactivated", 200


@app.route("/user/activate", methods=["POST"])
def user_activate():
    data = request.json
    user_record = db.session.query(AppUsers).filter(
        AppUsers.user_id == data["user_id"]).first()

    if user_record == None:
        return "user doesnt exist", 400

    user_record.active = True
    db.session.commit()
    return "user activated", 200


# if __name__ == "__main__":
#     create_all()
#     app.run(debug=True)
