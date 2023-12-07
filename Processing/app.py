import connexion
import yaml
import requests
import logging
import logging.config
import json
from apscheduler.schedulers.background import BackgroundScheduler
import datetime
import os

SERVICE_PORT = 8100
API_STAT_FILE = 'allergenscan_stats.yaml'
CONF_FILE = 'app_conf.yml'
LOG_FILE = 'log_conf.yml'

current_datetime = datetime.datetime.now()
current_datetime_str = current_datetime.strftime("%Y-%m-%d %H:%M:%S")

# Load configuration from YAML files
with open(CONF_FILE, 'r') as f:
    app_config = yaml.safe_load(f.read())

with open(LOG_FILE, 'r') as f:
    log_config = yaml.safe_load(f.read())
    logging.config.dictConfig(log_config)
logger = logging.getLogger('basicLogger')

# Determine the file path for data.json
datastore_filepath = app_config['datastore']['filename']

# Function to initialize or load stats from data.json
def initialize_or_load_stats():
    if not os.path.exists(datastore_filepath):
        logger.info("data.json does not exist. Creating one with default stats.")
        stats = {
            "num_allergen_alerts": 0,
            "num_ingredient_suggestions": 0,
            "num_symptoms_recorded": 0,
            "total_ingredient_substitutes": 0,
            "last_updated": current_datetime_str
        }
        with open(datastore_filepath, 'w') as f:
            logger.info("Default data.json values loaded...")
            json.dump(stats, f)
    else:
        logger.info("Data.json already exists! Loading data from data.json...")
        with open(datastore_filepath, 'r') as f:
            stats = json.load(f)
            logger.debug("data.json content loaded from existing file...")
    return stats

# Initialize a set to hold unique symptoms and ingredients
unique_symptoms = set()
unique_suggested_ingredients = set()

# Function to get stats
def get_stats():
    logger.info("Start GET /events/stats")
    stats = initialize_or_load_stats()

    # Log and return stats
    logger.info("End GET /events/stats")

    return stats, 200

# Function to populate data
def populate_data():
    
    try:
        # Before fetching new events, set last_updated to the current time
        stats = initialize_or_load_stats()
        #--------------------------------------------------------------------------------------------------------------------------
        timestamp = {"timestamp": stats['last_updated']}
        logger.info("Fetching allergen_alert event...")
        response_allergen = requests.get(f"{app_config['eventstore']['url']}/allergen_alert/readings", params=timestamp)
        # Process Allergen Alerts
        if response_allergen.status_code == 200:
            logger.info("Processing allergen alerts...")
            logger.debug(f"timestamp used for response_allergen:{stats['last_updated']}")
            new_events_allergen_alert = response_allergen.json()
            allergen_events = len(new_events_allergen_alert)
            
            stats['num_allergen_alerts'] = allergen_events
            unique_symptoms.update(event.get('symptom', None) for event in new_events_allergen_alert)
            logger.debug(f"Current num_allergen_alerts: {stats['num_allergen_alerts']}")
        #-------------------------------------------------------------------------------------------------------------------------- 
        # Fetch new events based on the last_processed time for Allergen Alerts
        timestamp = {"timestamp": stats['last_updated']}
        logger.info("Fetching ingredient_suggestion/readings event...")
        response_ingredient = requests.get(f"{app_config['eventstore']['url']}/ingredient_suggestion/readings", params=timestamp)
        
        # Process Ingredient Suggestions
        if response_ingredient.status_code == 200:
            logger.info("Processing ingredient suggestions...")
            logger.debug(f"timestamp used for response_allergen:{stats['last_updated']}")
            new_events_ingredient_suggestion = response_ingredient.json()
            ingredient_events = len(new_events_ingredient_suggestion)
            
            stats['num_ingredient_suggestions'] = ingredient_events
            unique_suggested_ingredients.update(event.get('suggested_ingredient', None) for event in new_events_ingredient_suggestion)
            logger.debug(f"Current num_ingredient_suggestions: {stats['num_ingredient_suggestions']}")
        #--------------------------------------------------------------------------------------------------------------------------
        # Update other stats
        logger.info("\nUpdating Stats...")
        stats['num_symptoms_recorded'] = len(unique_symptoms)
        stats['total_ingredient_substitutes'] = len(unique_suggested_ingredients)
        stats['last_updated'] = current_datetime_str
        logger.debug(f"Updated time:{stats['last_updated']}")

        # Write the updated statistics to data.json
        with open(datastore_filepath, 'w') as f:
            logger.debug(f"Saving updated stats --> {stats}")
            json.dump(stats, f)
        logger.info("Successfully wrote updated stats to data.json")

    except Exception as e:
        logger.error("An error occurred: {}".format(str(e)))

        


# Initialize scheduler
def init_scheduler():
    sched = BackgroundScheduler(daemon=True)
    sched.add_job(populate_data, 'interval', seconds=app_config['scheduler']['period_sec'])
    sched.start()

app = connexion.FlaskApp(__name__, specification_dir='')
app.add_api(API_STAT_FILE,
        strict_validation=True,
        validate_responses=True)

if __name__ == "__main__":
    init_scheduler()
    app.run(port=SERVICE_PORT)
