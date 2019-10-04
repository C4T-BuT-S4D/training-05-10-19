from app import db
from pony import orm


class User(db.Entity):
    id = orm.PrimaryKey(int, auto=True)
    login = orm.Required(str, unique=True)
    password = orm.Required(str)
    messages = orm.Set('Message')
    uploads = orm.Set('File')


class Thread(db.Entity):
    id = orm.PrimaryKey(int, auto=True)
    name = orm.Required(str)
    messages = orm.Set('Message')


class Message(db.Entity):
    id = orm.PrimaryKey(int, auto=True)
    text = orm.Required(str)
    thread = orm.Required(Thread)
    author = orm.Required(User)


class File(db.Entity):
    id = orm.PrimaryKey(int, auto=True)
    filename = orm.Required(str)
    user = orm.Required(User)
