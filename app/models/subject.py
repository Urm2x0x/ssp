from app.extensions import db

#Main scope of this file : We created the following Columns in a table
#ID (primary key)
#User_id (foreign key)
#name 
#exam-date


#Creating Subject table using Our class, we defined in extensions.py and also i created one table previously in user.py
class Subject(db.Model):

    __tablename__ = "subjects"
    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    name = db.Column(db.String(120), nullable=False)

    exam_date = db.Column(db.Date, nullable=True)

    #db.relationship returns a python list
    topics = db.relationship(
        "Topic", backref="subject", cascade="all, delete-orphan",
        order_by="Topic.syllabus_order",
    )

    def __repr__(self): #String Representation btw
        return f"<Subject {self.id} {self.name}>"