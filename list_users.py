from flask_app import db, User, app

def list_all_users():
    with app.app_context():
        users = User.query.all()
        print(f"Found {len(users)} users:\n")
        for user in users:
            print(f"ID: {user.id}, Username: {user.username}, Password Hash: {user.password}")

if __name__ == "__main__":
    list_all_users()
