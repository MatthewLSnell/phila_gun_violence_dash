"""
This script is used to interact with a PostgreSQL database
using SQLAlchemy. It inserts data into the database
from a specified URL and prints information about the table.
"""

import os
import pandas as pd
import io
import requests
from sqlalchemy import VARCHAR, Column, Integer, DateTime, Float, BigInteger
from sqlalchemy.orm import declarative_base
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select
from sqlalchemy.dialects import postgresql
from urllib.parse import quote_plus
from dotenv import load_dotenv
from datetime import datetime


def get_db_params():
    """
    Load database parameters from environment variables
    and return as a dictionary.
    """
    load_dotenv()
    return {
        "host": os.getenv("DB_HOST"),
        "database": os.getenv("DB_NAME"),
        "user": os.getenv("DB_USER"),
        "password": quote_plus(os.getenv("DB_PASS")),
        "port": os.getenv("DB_PORT"),
    }


db_params = get_db_params()

Base = declarative_base()


def start_session():
    """
    Start a new session with the PostgreSQL database.
    Returns the session object.
    """
    engine = create_engine(
        f'postgresql://{db_params["user"]}:{db_params["password"]}@{db_params["host"]}:{db_params["port"]}/{db_params["database"]}'
    )
    session = sessionmaker(bind=engine)
    Base.metadata.create_all(engine)
    return session()


class PHL_SHOOTING(Base):
    __tablename__ = "phl_shooting"
    date_inserted = Column(DateTime)
    date_updated = Column(DateTime)
    the_geom = Column(VARCHAR)
    the_geom_webmercator = Column(VARCHAR)
    objectid = Column(BigInteger, primary_key=True, nullable=False)
    year = Column(Integer)
    dc_key = Column(Float)
    code = Column(Float)
    date_ = Column(VARCHAR)
    time = Column(VARCHAR)
    race = Column(VARCHAR)
    sex = Column(VARCHAR)
    age = Column(Float)
    wound = Column(VARCHAR)
    officer_involved = Column(VARCHAR)
    offender_injured = Column(VARCHAR)
    offender_deceased = Column(VARCHAR)
    location = Column(VARCHAR)
    latino = Column(Float)
    point_x = Column(Float)
    point_y = Column(Float)
    dist = Column(Float)
    inside = Column(Float)
    outside = Column(Float)
    fatal = Column(Float)
    lat = Column(Float)
    lng = Column(Float)

    def __repr__(self):
        return str([getattr(self, c.name, None) for c in self.__table__.c])


def fetch_data(url):
    """
    Fetch data from the provided URL and return as a list of dictionaries.
    Adds current time to 'date_inserted' and 'date_updated' fields.
    """
    response = requests.get(url)
    response.raise_for_status()

    data = pd.read_csv(io.StringIO(response.text))
    current_time = datetime.now()  # get current time

    data["date_inserted"] = current_time
    data["date_updated"] = current_time

    return data.to_dict("records")


def upsert(session, model, rows, as_of_date_col="objectid", no_update_cols=[]):
    """
    Perform an upsert (update or insert) operation on the specified table.
    If a row with the same objectid already exists, it updates the row.
    If it does not exist, it inserts a new row.
    """
    table = model.__table__

    stmt = insert(table).values(rows)

    no_update_cols.extend(["date_inserted", "date_updated"])

    update_cols = [
        c.name
        for c in table.c
        if c not in list(table.primary_key.columns) and c.name not in no_update_cols
    ]

    current_time = datetime.now()
    set_dict = {k: getattr(stmt.excluded, k) for k in update_cols}
    set_dict["date_updated"] = current_time

    on_conflict_stmt = stmt.on_conflict_do_update(
        index_elements=table.primary_key.columns,
        set_=set_dict,
        index_where=(
            getattr(model, as_of_date_col) != getattr(stmt.excluded, as_of_date_col)
        ),
    )

    session.execute(on_conflict_stmt)


def print_table_info(session, table):
    """Prints the number of rows, columns, and date of last update in a SQL table."""
    # Query all rows from the table
    rows = session.query(table).all()

    # Calculate the number of rows
    num_rows = len(rows)

    # Calculate the number of columns
    num_columns = len(rows[0].__table__.columns) if rows else 0

    # Find the date of the last update
    last_update = max(row.date_updated for row in rows) if rows else None

    print(f"Number of rows: {num_rows:,}")
    print(f"Number of columns: {num_columns}")
    print(f"Date of last update: {last_update}")
    
def get_dataframe(session, table):
    """
    Query all rows from a SQL table and return a pandas DataFrame.

    Parameters:
    - session: The SQLAlchemy session object
    - table: The SQLAlchemy table object

    Returns:
    - df: A pandas DataFrame containing the SQL table data
    """
    # Define a select statement
    stmt = select(table)

    # Execute the statement and fetch all results
    results = session.execute(stmt).fetchall()

    # Create a dataframe from the results
    df = pd.read_sql(stmt, session.bind)

    return df


if __name__ == "__main__":
    session = start_session()

    url = "https://phl.carto.com/api/v2/sql?q=SELECT+*,+ST_Y(the_geom)+AS+lat,+ST_X(the_geom)+AS+lng+FROM+shootings&filename=shootings&format=csv&skipfields=cartodb_id"

    # Fetch the data from the url
    rows = fetch_data(url)

    print("\nBefore Upsert:\n")
    print_table_info(session, PHL_SHOOTING)

    # Perform the upsert operation
    upsert(session, PHL_SHOOTING, rows, "objectid")
    session.commit()

    print("\nAfter upsert:\n")
    print_table_info(session, PHL_SHOOTING)
    
    # Use the function to query the table and create a dataframe
    df = get_dataframe(session, PHL_SHOOTING)
    
    # Print the first five rows of the dataframe
    print("\n" + str(df.head()))
