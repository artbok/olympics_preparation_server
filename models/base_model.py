from peewee import SqliteDatabase


db = SqliteDatabase('data.db')


class BaseModel(db.Model):
    class Meta:
        database = db
        only_save_dirty = True