from datetime import datetime, timezone
from app.extensions import db

 #creating a table using db class. that is our model user will inherit from this class db
class User(db.Model):
    __tablename__ = "users"
    #creating columns id(primary key), name,email,password_hash,goal(competetive exam, semester etc), study hours and daily hours
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    goal = db.Column(db.String(50), nullable=True)

    weekday_hours = db.Column(db.Float, nullable=False, default=3.0)
    weekend_hours = db.Column(db.Float, nullable=False, default=4.0)

    easy_topic_hours = db.Column(db.Float, nullable=False, default=2.5)
    medium_topic_hours = db.Column(db.Float, nullable=False, default=4.0)
    hard_topic_hours = db.Column(db.Float, nullable=False, default=6.0)

    has_seen_tutorial = db.Column(db.Boolean, nullable=False, default=False)

    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    #setting up relationship with subjects table
    subjects = db.relationship("Subject", backref="user", cascade="all, delete-orphan")

    #this function takes self as an input and returns 
    def __repr__(self):
        return f"<User {self.id} {self.email}>"
