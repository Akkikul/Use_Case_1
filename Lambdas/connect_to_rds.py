import logging
import pymysql
import os
from Model.rds_config import get_secrets

# rds settings
secrets = get_secrets()
username = secrets['username']
password = secrets['password']
dbname = secrets['dbname']
host = os.environ['HOST']

logger = logging.getLogger()
logger.setLevel(logging.INFO)

conn = pymysql.connect(host, user=username, passwd=password, db=dbname, connect_timeout=5)


def create_tables():
    try:
        create_query = f"CREATE TABLE {dbname}.Account ( account_id INT(10) AUTO_INCREMENT PRIMARY KEY,\
					   customer_id INT(10), reg_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP)"
        with conn.cursor() as cur:
            cur.execute(create_query)
        conn.commit()
    finally:
        conn.close()


def insert_into_tables():
    try:
        insert_query = f"insert into {dbname}.Customer (first_name, last_name) values('Arun', 'Kulkarni')"
        with conn.cursor() as cur:
            cur.execute(insert_query)
        conn.commit()
    finally:
        conn.close()


def connect(event, context):
    create_tables()
    # insert_into_tables()
