"""The database engine."""

import os.path
from sqlalchemy import create_engine
from ..app import data_dir

engine = create_engine('sqlite:///%s' % os.path.join(data_dir, 'db.sqlite3'))
