import sys
import os
import logging
import pymysql
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


def get_transaction(event, context):
    # TODO implement
    """
    This function fetches content from MySQL RDS instance """

    item_count = 0
    query_stmt = f"select count(Transaction_ID) from Transaction where Customer_ID = {event['Customer_ID']}"
    with conn.cursor() as cur:
        item_count = cur.execute(query_stmt)
    conn.commit()

    return {"Transaction Count": item_count}

