from sqlalchemy import create_engine
import pandas as pd

import os
from dotenv import load_dotenv

import platform

load_dotenv()

#mapping for database connection
sql_username = os.getenv('USERNAME')
sql_password = os.getenv('PASSWORD')
sql_host = os.getenv('HOSTNAME')
sql_database = os.getenv('DATABASE')

url_string = f"mysql+pymysql://{sql_username}:{sql_password}@{sql_host}:3306/{sql_database}"

conn = create_engine(url_string)

sql_toexecute = """
  select *
  from research_experiment_refactor_test
  limit 50;
  """

response = pd.read_sql(sql_toexecute, conn)
response