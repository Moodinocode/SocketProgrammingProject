from flask_app import db, User, app
from flask_bcrypt import Bcrypt

bcrypt = Bcrypt(app)

def update_normal_users():
    with app.app_context():
        # Create the database tables if they don't exist
        db.create_all()
        
        # Remove the original 'user' account
        # Remove all existing "Ayman Tajeddine" users
        existing_aymans = User.query.filter_by(username="Ayman Tajjedine").all()
        for user in existing_aymans:
          db.session.delete(user)
          print(f"Removed duplicate user: {user.username}")

          # If you want to delete anyone named exactly "Ayman" too (optional)
        existing_ayman = User.query.filter_by(username="Ayman").all()
        for user in existing_ayman:
            db.session.delete(user)
            print(f"Removed duplicate user: {user.username}")

        
        db.session.commit()
        
        # List of normal users to add with unique passwords
        normal_users = [
            #{"username": "Ayman Tajeddine", "password": "networksOnTop"},
            # {"username": "Mohammad Jomha", "password": "CP3ezA"},
            # {"username": "Alice", "password": "whereIsBob"}
        ]
        
        # Add each user to the database
        for user_data in normal_users:
            # Hash the password
            hashed_password = bcrypt.generate_password_hash(user_data["password"]).decode('utf-8')
            # Create new user
            new_user = User(username=user_data["username"], password=hashed_password)
            db.session.add(new_user)
            print(f"Added user: {user_data['username']} with unique password")
        
        # Commit the changes
        db.session.commit()
        print("All users have been updated successfully!")

if __name__ == "__main__":
    update_normal_users() 