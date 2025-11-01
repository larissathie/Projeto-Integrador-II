from app import app, db
from sqlalchemy import inspect
import os

print('DB ->', os.path.abspath('database.db'))

with app.app_context():
    db.create_all()
    print('✅ Tabelas:', inspect(db.engine).get_table_names())
