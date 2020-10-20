from Pony.orm import *

db = Database()
db.bind(provider='sqlite', filename='secretVoldemort.sqlite', create_db=True)

# Agregar entidades antes del mapping



#

db.generate_mapping(create_tables=True)
