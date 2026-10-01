from app.extensions import db

#we are creating a table for OR_Tools here
#id (primary key)
#topic id (foreign key)
#scheduled date
#duration minutes
#completed

class StudySession(db.Model):

    __tablename__ = "study_sessions"

    id = db.Column(db.Integer, primary_key=True)
    topic_id = db.Column(db.Integer, db.ForeignKey("topics.id"), nullable=False)
    scheduled_date = db.Column(db.Date, nullable=False)
    duration_minutes = db.Column(db.Integer, nullable=False)
    completed = db.Column(db.Boolean, default=False)

    def __repr__(self):
        return f"<StudySession {self.id} topic={self.topic_id} {self.scheduled_date}>"