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
from models.app_lanes import AppLanes, lane_schema, lanes_schema
from models.app_tasks import AppTasks, task_schema, tasks_schema
from models.app_users import AppUsers, user_schema, users_schema
from db import db

app = Flask(__name__)

database_host = "127.0.0.1:5432"
database_name = "task_manager"
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://tnjapnudtdxjee:cd6f1837429535509d6fbbcb3f0dd2393f67ad9f522e1ac81b369a77d1b0b0a7@ec2-3-223-169-166.compute-1.amazonaws.com:5432/d3v1krq3omoim7'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

ma = Marshmallow(app)


def create_all():
    db.init_app(app)
    with app.app_context():
        db.create_all()

        print('Querying for Tony Stark...')
        admin_data = db.session.query(AppUsers).filter(
            AppUsers.email == "tony@gmail.com").first()

        if admin_data == None:
            print("Tony Stark not found! Creating tony@gmail.com user...")
            password = '1234'

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
