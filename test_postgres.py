'''
### Check Connection to Postgres
from sqlalchemy import create_engine, text

engine = create_engine(
    "postgresql://superset:superset@localhost:5432/beam_monitor"
)

with engine.connect() as conn:
    print("Conectado a beam_monitor")

'''

'''
### Check if we can read from the "runs" table
from sqlalchemy import create_engine, text

engine = create_engine(
    "postgresql://superset:superset@localhost:5432/beam_monitor"
)

with engine.connect() as conn:
    print(
        conn.execute(
            text("SELECT COUNT(*) FROM runs")
        ).fetchone()
    )

'''


#Delete and recreate the database
from sqlalchemy import create_engine, text

engine = create_engine(
    "postgresql://superset:superset@localhost:5432/postgres"
)

with engine.connect().execution_options(isolation_level="AUTOCOMMIT") as conn:
    conn.execute(text("DROP DATABASE IF EXISTS beam_monitor"))
    conn.execute(text("CREATE DATABASE beam_monitor"))


'''
from sqlalchemy import create_engine
import pandas as pd

engine = create_engine(
    "postgresql://superset:superset@localhost:5432/beam_monitor"
)

print(pd.read_sql("SELECT * FROM runs", engine))
'''