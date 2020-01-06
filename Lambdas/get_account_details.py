import pymysql
import os
import logging
import sys
from Model.rds_config import get_secrets


# rds settings
secrets = get_secrets()
username = secrets['username']
password = secrets['password']
dbname = secrets['dbname']
host = os.environ['HOST']

logger = logging.getLogger()
logger.setLevel(logging.INFO)

try:
    conn = pymysql.connect(host, user=username, passwd=password, db=dbname, connect_timeout=5) 
except pymysql.MySQLError as e:
    logger.error("ERROR: Unexpected error: Could not connect to MySQL instance.")
    logger.error(e)
    sys.exit()
logger.info("SUCCESS: Connection to RDS MySQL instance succeeded")


def get_account(event, context):
    """
    This function fetches content from MySQL RDS instance
    """
    query_stmt = f"select * from Account where Customer_ID = {event['Customer_ID']}"
    with conn.cursor() as cur:
        cur.execute(query_stmt)
        rows = cur.fetchall()
    conn.commit()

    for item in rows:
        return {"Account ID": item[0], "Customer ID": item[1]}
