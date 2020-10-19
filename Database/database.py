from pony import orm
from db_user import create_user_entity

db = orm.Database()

db.bind(provider='sqlite', filename='secretVoldemort.sqlite', create_db=True)
user_entity = create_user_entity(db, orm)

db.generate_mapping(create_tables=True)


