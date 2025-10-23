from sqlalchemy import create_engine
import pandas as pd
import os
from dotenv import load_dotenv

load_dotenv()

# mapping for database connection
# need to rename the username since it conflicts with a reserved word windows

sql_username = os.getenv('POWERUSER')
sql_password = os.getenv('PASSWORD')
sql_host = os.getenv('HOSTNAME')
sql_database = os.getenv('DATABASE')

sql_username

url_string = f"mysql+pymysql://{sql_username}:{sql_password}@{sql_host}:3306/{sql_database}"

conn = create_engine(url_string)

# remove limit 50; to get full dataset
sql_toexecute = """
  select *
  from research_experiment_refactor_test
  limit 50; 
  """

response = pd.read_sql(sql_toexecute, conn)
response

## Downloading the data locally
# Ensure 'raw' folder exists
raw_folder = "raw"
os.makedirs(raw_folder, exist_ok=True)

#Save result to CSV in 'raw' folder
output_path = os.path.join(raw_folder, "query_result.csv")
response.to_csv(output_path, index=False)

print(f"Query result saved to: {output_path}")
