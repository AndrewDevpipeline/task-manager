from app import app, create_all, db

db.init_app(app)

if __name__ == "__main__":
    create_all()

    app.run()
