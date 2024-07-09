from database import Base, engine
from models import FormData, Client, Message


def init_db() -> None:
    Base.metadata.create_all(bind=engine)
    FormData.metadata.create_all(bind=engine)
    Client.metadata.create_all(bind=engine)
    Message.metadata.create_all(bind=engine)
