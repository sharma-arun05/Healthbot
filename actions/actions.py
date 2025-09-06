from typing import Any, Text, Dict, List, Optional
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.forms import FormValidationAction
import requests
import os
import time
import logging
import sqlite3

# --- 1. Configuration and Logging ---
LOG = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

GOV_API_BASE = os.getenv("GOV_API_BASE", "https://example.gov.health/api")
TWILIO_NUMBER = os.getenv("TWILIO_NUMBER")
DATABASE_PATH = os.getenv("DATABASE_PATH", "subscriptions.db")

# --- 2. Helper Functions ---
def get_user_language(tracker: Tracker) -> str:
    return tracker.get_slot("language") or "en"

def retry_request(url: str, params: Optional[Dict] = None, lang: str = "en", timeout: int = 5, retries: int = 2) -> Dict:
    full_params = params or {}
    full_params["lang"] = lang
    for attempt in range(1, retries + 2):
        try:
            r = requests.get(url, params=full_params, timeout=timeout)
            r.raise_for_status()
            return r.json()
        except requests.exceptions.RequestException as e:
            LOG.warning("Request to '%s' failed (attempt %d/%d): %s", url, attempt, retries + 1, e)
            if attempt <= retries:
                time.sleep(1 * attempt)
            else:
                LOG.error("All retry attempts failed for URL: %s", url)
                raise
    return {}

def send_outbound_message(to_number: str, text: str) -> bool:
    account_sid = os.getenv("TWILIO_ACCOUNT_SID")
    auth_token = os.getenv("TWILIO_AUTH_TOKEN")
    if account_sid and auth_token and TWILIO_NUMBER:
        try:
            from twilio.rest import Client
            client = Client(account_sid, auth_token)
            message = client.messages.create(body=text, from_=TWILIO_NUMBER, to=to_number)
            LOG.info("Sent message %s to %s", message.sid, to_number)
            return True
        except ImportError:
            LOG.error("Twilio library not installed. Please run 'pip install twilio'.")
            return False
        except Exception as e:
            LOG.error("Failed to send message via Twilio: %s", e)
            return False
    else:
        LOG.info("Twilio credentials not configured. Stubbing message send to %s: %s", to_number, text)
        return True

class SubscriptionDB:
    def __init__(self, db_path: str):
        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        self.cursor = self.conn.cursor()
        self.cursor.execute(
            "CREATE TABLE IF NOT EXISTS subscribers (phone_number TEXT PRIMARY KEY, location TEXT, subscribed_at REAL)"
        )
        self.conn.commit()

    def add_subscriber(self, phone_number: str, location: str):
        self.cursor.execute(
            "INSERT OR REPLACE INTO subscribers (phone_number, location, subscribed_at) VALUES (?, ?, ?)",
            (phone_number, location, time.time())
        )
        self.conn.commit()
    
    def get_subscribers(self) -> List[Dict[str, Any]]:
        self.cursor.execute("SELECT phone_number, location FROM subscribers")
        rows = self.cursor.fetchall()
        return [{"phone_number": row[0], "location": row[1]} for row in rows]

db = SubscriptionDB(DATABASE_PATH)

# --- 4. Custom Actions ---
class ActionSetLanguage(Action):
    def name(self) -> Text:
        return "action_set_language"
    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        lang_entity = next(tracker.get_latest_entity_values("language_entity"), None)
        lang_map = {"hindi": "hi", "english": "en", "tamil": "ta"}
        lang_code = lang_map.get(lang_entity, "en")
        dispatcher.utter_message(response=f"utter_language_set_{lang_code}")
        return [tracker.update_slot("language", lang_code)]

class ActionProvideSymptomInfo(Action):
    def name(self) -> Text:
        return "action_provide_symptom_info"
    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        disease = next(tracker.get_latest_entity_values("disease"), None)
        lang = get_user_language(tracker)
        if not disease:
            dispatcher.utter_message(response=f"utter_ask_disease_{lang}")
            return []
        try:
            data = retry_request(f"{GOV_API_BASE}/diseases/{disease}/symptoms", lang=lang)
            summary = data.get("summary") or data.get("symptoms")
            if summary:
                dispatcher.utter_message(response=f"utter_symptom_info_{lang}", disease=disease, summary=summary)
            else:
                dispatcher.utter_message(response=f"utter_no_data_found_{lang}")
        except Exception:
            dispatcher.utter_message(response=f"utter_api_failure_{lang}")
        return []

class ActionProvideVaccineInfo(Action):
    def name(self) -> Text:
        return "action_provide_vaccine_info"
    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        age_group = tracker.get_slot("age_group") or "child"
        location = tracker.get_slot("location") or "national"
        lang = get_user_language(tracker)
        try:
            data = retry_request(f"{GOV_API_BASE}/vaccines/schedule", params={"age_group": age_group, "location": location}, lang=lang)
            schedule_info = data.get("summary") or "Please visit your nearest health center for the full schedule."
            dispatcher.utter_message(response=f"utter_vaccine_info_{lang}", age_group=age_group, location=location, schedule_info=schedule_info)
        except Exception:
            dispatcher.utter_message(response=f"utter_api_failure_{lang}")
        return []

class ActionProvidePrevention(Action):
    def name(self) -> Text:
        return "action_provide_prevention"
    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        disease = next(tracker.get_latest_entity_values("disease"), None)
        lang = get_user_language(tracker)
        try:
            data = retry_request(f"{GOV_API_BASE}/prevention/{disease}", lang=lang)
            summary = data.get("summary") or "General prevention: keep water stored safely, use insect repellent, get vaccinated."
            dispatcher.utter_message(response=f"utter_prevention_info_{lang}", summary=summary)
        except Exception:
            dispatcher.utter_message(response=f"utter_api_failure_{lang}")
        return []

class SubscriptionForm(FormValidationAction):
    def name(self) -> Text:
        return "subscription_form"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        phone_number = tracker.get_slot("phone_number")
        location = tracker.get_slot("location")
        lang = get_user_language(tracker)

        if phone_number and location:
            try:
                db.add_subscriber(phone_number, location)
                dispatcher.utter_message(response=f"utter_subscription_success_{lang}", phone_number=phone_number, location=location)
            except Exception as e:
                LOG.error(f"Failed to save subscription: {e}")
                dispatcher.utter_message(response=f"utter_subscription_failure_{lang}")
        return []