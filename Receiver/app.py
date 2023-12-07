import connexion
from connexion import NoContent
import yaml
import logging
import logging.config
import uuid
from pykafka import KafkaClient
import datetime
import json

MAX_EVENTS = 10
JSON_FILE = "event.json"
SERVICE_PORT = 8080
ALLERGEN_SCAN_API = "allergenscan_api.yaml"

# Load logging configuration from log_conf.yml
with open('log_conf.yaml', 'r') as f:
    log_config = yaml.safe_load(f.read())
    logging.config.dictConfig(log_config)
    
logger = logging.getLogger('basicLogger')

# Load app configuration from app_conf.yaml
with open('app_conf.yaml', 'r') as f:
    app_config = yaml.safe_load(f.read())
    
allergen_alert_url = app_config['allergen_alert_event']['url']
ingredient_suggestion_url = app_config['ingredient_suggestion']['url']

KAFKA_HOSTNAME = app_config['events']['hostname']
KAFKA_PORT = app_config['events']['port']
KAFKA_TOPIC = app_config['events']['topic']

def submit_allergen_alert(body):
    trace_id = str(uuid.uuid4()) 
    body["trace_id"] = trace_id

    logger.info(f"Received event Allergen_Alert request with a trace id of {trace_id}")

    client = KafkaClient(hosts=f"{KAFKA_HOSTNAME}:{KAFKA_PORT}")
    topic = client.topics[str.encode(KAFKA_TOPIC)]
    producer = topic.get_sync_producer()

    msg = {
        "type": "Allergen_Alert",
        "datetime": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "payload": body
    }
    msg_str = json.dumps(msg)
    producer.produce(msg_str.encode('utf-8'))
    logger.info("Sending allergen alert request to KAFKA...")
    return NoContent, 201
#--------------------------------------------------------
def submit_ingredient_suggestion(body):
    trace_id = str(uuid.uuid4())
    body["trace_id"] = trace_id

    logger.info(f"Received event Ingredient_Suggestion request with a trace id of {trace_id}")

    client = KafkaClient(hosts=f"{KAFKA_HOSTNAME}:{KAFKA_PORT}")
    topic = client.topics[str.encode(KAFKA_TOPIC)]
    producer = topic.get_sync_producer()

    msg = {
        "type": "Ingredient_Suggestion",
        "datetime": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "payload": body
    }
    msg_str = json.dumps(msg)
    producer.produce(msg_str.encode('utf-8'))
    logger.info("Sending ingredient suggestion request to KAFKA...")
    return NoContent, 201

app = connexion.FlaskApp(__name__, specification_dir=".")
app.add_api(ALLERGEN_SCAN_API, strict_validation=True, validate_responses=True)

if __name__ == "__main__":
    app.run(port=SERVICE_PORT)
