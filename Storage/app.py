import connexion
from connexion import NoContent
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from base import Base
from allergen_alert import AllergenAlert
from ingredient_suggestion import IngredientSuggestion
import datetime
import yaml
import logging
import logging.config
from pykafka import KafkaClient
from pykafka.common import OffsetType
from flask import Flask, jsonify
import threading
import json

# Constants
MAX_EVENTS = 10
JSON_FILE = "event.json"
SERVICE_PORT = 8090
ALLERGEN_SCAN_API = "allergenscan_api.yaml"

# Initialize logger
with open('log_conf.yaml', 'r') as f:
    log_config = yaml.safe_load(f.read())
    logging.config.dictConfig(log_config)
    logger = logging.getLogger('basicLogger')

# Load application configurations
with open('app_conf.yaml', 'r') as f:
    app_config = yaml.safe_load(f.read())

# Database configurations
MYSQL_USER = app_config['datastore']['user']
MYSQL_PASSWORD = app_config['datastore']['password']
MYSQL_HOSTNAME = app_config['datastore']['hostname']
MYSQL_PORT = app_config['datastore']['port']
MYSQL_DB = app_config['datastore']['db']

KAFKA_HOSTNAME = app_config['events']['hostname']
KAFKA_PORT = app_config['events']['port']
KAFKA_TOPIC = app_config['events']['topic']

logger.info(f"Connecting MySQL DB on {MYSQL_HOSTNAME} at port {MYSQL_PORT}...")

# Database URL
DATABASE_URL = f"mysql+pymysql://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_HOSTNAME}:{MYSQL_PORT}/{MYSQL_DB}"

# Initialize database engine and session
DB_ENGINE = create_engine(DATABASE_URL)
Base.metadata.bind = DB_ENGINE
DB_SESSION = sessionmaker(bind=DB_ENGINE)

def submit_allergen_alert(body):
    """Receives an allergen alert and stores it into the database."""
    session = DB_SESSION()

    a_a = AllergenAlert(
        body['user_id'],
        body['user_name'],
        body['barcode'],
        body['product_name'],
        body['allergen'],
        body['symptom'],
        body['trace_id']
    )

    session.add(a_a)
    session.commit()
    session.close()

    logger.debug(f"Stored event AllergenAlert request with a trace id of {body['trace_id']}")
    return NoContent, 201

def submit_ingredient_suggestion(body):
    """Receives an ingredient suggestion and stores it into the database."""
    session = DB_SESSION()

    i_s = IngredientSuggestion(
        body['user_id'],
        body['user_name'],
        body['barcode'],
        body['product_name'],
        body['suggested_ingredient'],
        body['suggestion_details'],
        body['trace_id']
    )

    session.add(i_s)
    session.commit()
    session.close()

    logger.debug(f"Stored event IngredientSuggestion request with a trace id of {body['trace_id']}")
    return NoContent, 201



def get_allergen_alerts(timestamp):
    """Gets AllergenAlert events after the specified timestamp."""
    session = DB_SESSION()
    timestamp_datetime = datetime.datetime.strptime(timestamp, "%Y-%m-%d %H:%M:%S")
    alerts = session.query(AllergenAlert).filter(AllergenAlert.date_created >= timestamp_datetime)
    result_list = []
    for alert in alerts:
        result_list.append(alert.to_dict())
    session.close()
    
    logger.debug(f"Received timestamp: {timestamp}")
    return result_list, 200

def get_ingredient_suggestions(timestamp):
    """Gets IngredientSuggestion events after the specified timestamp."""
    session = DB_SESSION()
    timestamp_datetime = datetime.datetime.strptime(timestamp, "%Y-%m-%d %H:%M:%S")
    suggestions = session.query(IngredientSuggestion).filter(IngredientSuggestion.date_created >= timestamp_datetime)
    result_list = []
    for suggestion in suggestions:
        result_list.append(suggestion.to_dict())
    session.close()
    
    logger.debug(f"Received timestamp: {timestamp}")
    return result_list, 200

def process_messages():
    hostname = "%s:%d" % (KAFKA_HOSTNAME, KAFKA_PORT)
    client = KafkaClient(hosts=hostname)
    topic = client.topics[str.encode(KAFKA_TOPIC)]

    consumer = topic.get_simple_consumer(consumer_group=b'event_group', reset_offset_on_start=False, auto_offset_reset=OffsetType.LATEST)

    for msg in consumer:
        msg_str = msg.value.decode('utf-8')
        msg = json.loads(msg_str)
        logger.info(f"Received Message: {msg}")
        
        session = DB_SESSION()
        
        payload = msg["payload"]
        if msg["type"] == "AllergenAlert":
            a_a = AllergenAlert(
                payload['user_id'],
                payload['user_name'],
                payload['barcode'],
                payload['product_name'],
                payload['allergen'],
                payload['symptom'],
                payload['trace_id']
            )
            session.add(a_a)
        
        elif msg["type"] == "Ingredient_Suggestion":
            i_s = IngredientSuggestion(
                payload['user_id'],
                payload['user_name'],
                payload['barcode'],
                payload['product_name'],
                payload['suggested_ingredient'],
                payload['suggestion_details'],
                payload['trace_id']
            )
            session.add(i_s)

        session.commit()
        session.close()
        consumer.commit_offsets()

# Initialize and run the application
app = connexion.FlaskApp(__name__, specification_dir=".")
app.add_api(ALLERGEN_SCAN_API, strict_validation=True, validate_responses=True)

if __name__ == "__main__":
    t1 = threading.Thread(target=process_messages)
    t1.setDaemon(True)
    t1.start()
    app.run(port=SERVICE_PORT)
