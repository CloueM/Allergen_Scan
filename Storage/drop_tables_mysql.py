import mysql.connector
import yaml

with open('app_conf.yaml', 'r') as f:
    app_config = yaml.safe_load(f)

MYSQL_USER = app_config['datastore']['user']
MYSQL_PASSWORD = app_config['datastore']['password']
MYSQL_HOSTNAME = app_config['datastore']['hostname']
MYSQL_PORT = app_config['datastore']['port']
MYSQL_DB = app_config['datastore']['db']

db_conn = mysql.connector.connect(
    host=MYSQL_HOSTNAME,
    user=MYSQL_USER,
    password=MYSQL_PASSWORD,
    database=MYSQL_DB,
    port=MYSQL_PORT
)


db_cursor = db_conn.cursor()

# Drop allergen_alert and ingredient_suggestion tables
db_cursor.execute('DROP TABLE allergen_alert, ingredient_suggestion')

db_conn.commit()
db_conn.close()
