from config.database import Base, engine
from models.form_data import FormData
from models.client import Client
from models.message import Message
from models.report import Report
from models.user import User


def init_db() -> None:
    Base.metadata.create_all(bind=engine)
    FormData.metadata.create_all(bind=engine)
    Client.metadata.create_all(bind=engine)
    Message.metadata.create_all(bind=engine)
    Report.metadata.create_all(bind=engine)
    User.metadata.create_all(bind=engine)
