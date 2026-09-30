import os
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker, declarative_base
import sqlalchemy as sa


#Documentation - for the above functions

#what does this file does is it stores variables used by our models. also for creating session.

BASE_DIR = os.path.abspath(os.path.dirname(__file__)) #__file__ python variable which fills automically, for where the current file is being run
# abs path converts .../app/ (stripped off the actual name)
INSTANCE_DIR = os.path.join(BASE_DIR, "..", "instance")
#.../app/instance 
os.makedirs(INSTANCE_DIR, exist_ok=True) #Os creates the new path

ENGINE_URL = f"sqlite:///{os.path.join(INSTANCE_DIR, 'app.db')}" #we are using sqlite, creating db

#creating a connection base with the database
engine = create_engine(
ENGINE_URL,
connect_args={"check_same_thread": False},
)

#to create sessions (read or write), we gonna have to use session maker
_SessionFactory = sessionmaker(bind=engine, autoflush=False, autocommit=False)
_ScopedSession = scoped_session(_SessionFactory) #creating threads for each user/ or their private session

#creating parent class - each file (user, topics gonna be created on this model)
Base = declarative_base()
Base.query = _ScopedSession.query_property() #query attribute for each table in models

#just creating a Class, this class gathers all function we would be needing for /app/models, so it just really a function used created for summing up of all the parts, needed by sql alqhemy in one place
class _DB:

    Model = Base #db.base just another name for table
    session = _ScopedSession #creates session/thread

    Column = sa.Column #the base gonna have these attributes
    Integer = sa.Integer
    String = sa.String
    Float = sa.Float
    Boolean = sa.Boolean
    Date = sa.Date
    DateTime = sa.DateTime
    ForeignKey = sa.ForeignKey

    @staticmethod
    def relationship(*args, **kwargs):
        from sqlalchemy.orm import relationship as _relationship
        return _relationship(*args, **kwargs)

    @staticmethod
    def create_all():
        Base.metadata.create_all(bind=engine)

    @staticmethod
    def remove_session():
        _ScopedSession.remove()


db = _DB()

#Thank you for looking at this pile of code, nobody was gonna look at it, but u did, thanks again bud.