from app.extensions import db

#We created the following Columns in this table
#ID (primary key)
#Subject_id (foreign key)
#name 
#unit name
#syllabus order
#difficulty
#exam date
#status
#hours remaining
#study sessions

class Topic(db.Model):

    __tablename__ = "topics"

    id = db.Column(db.Integer, primary_key=True)
    subject_id = db.Column(db.Integer, db.ForeignKey("subjects.id"), nullable=False)
    name = db.Column(db.String(120), nullable=False)

    unit_name = db.Column(db.String(160), nullable=True)

    syllabus_order = db.Column(db.Integer, nullable=False, default=0)

    difficulty = db.Column(db.Integer, nullable=False, default=2)

    exam_date = db.Column(db.Date, nullable=True)

    status = db.Column(db.String(20), nullable=False, default="not_yet_quizzed")

    hours_remaining = db.Column(db.Float, nullable=True, default=None)

    study_sessions = db.relationship(
        "StudySession", backref="topic", cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<Topic {self.id} {self.name} status={self.status}>"