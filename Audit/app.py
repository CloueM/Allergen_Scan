import connexion
import yaml
import uuid
import logging
import logging.config
import datetime
import requests
import json
from pykafka import KafkaClient
from pykafka.common import OffsetType
from connexion import NoContent
from flask_cors import CORS, cross_origin
import os 

current_datetime = datetime.datetime.now()
current_datetime_str = current_datetime.strftime("%Y-%m-%d %H:%M:%S")

MAX_EVENTS = 10
SERVICE_PORT = 8110
YAML_FILE = "allergenscan_api.yaml"

if "TARGET_ENV" in os.environ and os.environ["TARGET_ENV"] == "test":
    print("In Test Environment")
    app_conf_file = "/config/app_conf.yaml"
    log_conf_file = "/config/log_conf.yaml"
else:
    print("In Dev Environment")
    app_conf_file = "app_conf.yaml"
    log_conf_file = "log_conf.yaml"

# Load application configurations
with open(app_conf_file, 'r') as f:
        app_config = yaml.safe_load(f.read())

with open(log_conf_file, 'r') as f:
        log_config = yaml.safe_load(f.read())
        logging.config.dictConfig(log_config)

logger = logging.getLogger('basicLogger')

logger.info("App Conf File: %s" % app_conf_file)
logger.info("Log Conf File: %s" % log_conf_file)

KAFKA_HOSTNAME = app_config['events']['hostname']
KAFKA_PORT = app_config['events']['port']
KAFKA_TOPIC = app_config['events']['topic']

# Create a logger
logger = logging.getLogger('basicLogger')

def get_allergen_alerts(index):
    """ Get AllergenAlert events after a specific timestamp """

    # Initialize Kafka client
    hostname = f"{KAFKA_HOSTNAME}:{KAFKA_PORT}"
    client = KafkaClient(hosts=hostname)
    topic = client.topics[bytes(KAFKA_TOPIC, 'utf-8')]

    # Create a Kafka consumer
    consumer = topic.get_simple_consumer(reset_offset_on_start=True, auto_offset_reset=OffsetType.LATEST,consumer_timeout_ms=1000)

    logger.info(f"Retrieving AllergenAlert at index {index}")
    try:
        for msg in consumer:
            msg_str = msg.value.decode('utf-8')
            msg = json.loads(msg_str)

            # Check if the event type matches and decrement index until it reaches 0
            if msg.get("type") == "AllergenAlertEvent":
                if index == 0:
                    return msg, 200
                index -= 1
            logger.info(f"Audit - Received Allergen Alert: Type: {msg['type']}, Index: {index}, Details: {msg}")
        # If no event found at the specified index
        return {"message": "Not Found"}, 404

    except Exception as e:
        return {"message": "Internal Server Error"}, 500
    

def get_ingredient_suggestions(index):
    """ Get IngredientSuggestion events after a specific timestamp """
    # Initialize Kafka client
    hostname = f"{KAFKA_HOSTNAME}:{KAFKA_PORT}"
    client = KafkaClient(hosts=hostname)
    topic = client.topics[bytes(KAFKA_TOPIC, 'utf-8')]

    # Create a Kafka consumer
    consumer = topic.get_simple_consumer(reset_offset_on_start=True, auto_offset_reset=OffsetType.LATEST,consumer_timeout_ms=1000)

    logger.info(f"Retrieving IngredientSuggestion at index {index}")

    try:
        for msg in consumer:
            msg_str = msg.value.decode('utf-8')
            msg = json.loads(msg_str)

            # Check if the event type matches and decrement index until it reaches 0
            if msg.get("type") == "IngredientSuggestionEvent":
                if index == 0:
                    return msg, 200
                index -= 1
            logger.info(f"Audit - Received Ingredients Suggestion: Type: {msg['type']}, Index: {index}, Details: {msg}")
        # If no event found at the specified index
        return {"message": "Not Found"}, 404

    except Exception as e:
        logger.error(f"Error retrieving IngredientSuggestion events: {str(e)}")
        return {"message": "Internal Server Error"}, 500

# Create a Connexion app
app = connexion.FlaskApp(__name__, specification_dir='')
CORS(app.app)
app.app.config['CORS_HEADERS'] = 'Content-Type'
app.add_api(YAML_FILE, 
        strict_validation=True,
        validate_responses=True)

if __name__ == "__main__":
    app.run(port=SERVICE_PORT)
