from peewee import *

db = SqliteDatabase('boxes.db')

class Schedule(Model):
    id = PrimaryKeyField()
    medicineName = CharField()
    boxName = CharField()
    afterWhat = CharField()
    numberTabs = IntegerField()

    class Meta:
        database = db

class logs(Model):
    id = PrimaryKeyField()
    message = CharField()

    class Meta:
        database = db

def initialize_db():
    db.connect()
    db.create_tables([Schedule, logs] , safe = True)
    db.close()