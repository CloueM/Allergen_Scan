import mysql
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

# Create allergen_alert table
db_cursor.execute('''
CREATE TABLE allergen_alert
(id INT NOT NULL AUTO_INCREMENT,
 user_id INTEGER NOT NULL,
 user_name VARCHAR(250) NOT NULL,
 barcode BIGINT NOT NULL,
 product_name VARCHAR(250) NOT NULL,
 allergen VARCHAR(250) NOT NULL,
 symptom VARCHAR(250) NOT NULL,
 date_created VARCHAR(100) NOT NULL,
 trace_id VARCHAR(36),
 PRIMARY KEY (id))
''')

# Create ingredient_suggestion table
db_cursor.execute('''
CREATE TABLE ingredient_suggestion
(id INT NOT NULL AUTO_INCREMENT,
 user_id INTEGER NOT NULL,
 user_name VARCHAR(250) NOT NULL,
 barcode BIGINT NOT NULL,
 product_name VARCHAR(250) NOT NULL,
 suggested_ingredient VARCHAR(250) NOT NULL,
 suggestion_details VARCHAR(250) NOT NULL,
 date_created VARCHAR(100) NOT NULL,
 trace_id VARCHAR(36),
 PRIMARY KEY (id))
''')

db_conn.commit()
db_conn.close()
