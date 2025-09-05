from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
import requests, datetime

class ActionGetSymptoms(Action):
    def name(self) -> Text:
        return "action_get_symptoms"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        disease = next(tracker.get_latest_entity_values("disease"), None)
        if disease:
            response = f"Common symptoms of {disease} include fever, headache, and fatigue. Please consult a doctor if severe."
        else:
            response = "Please specify the disease."
        dispatcher.utter_message(text=response)
        return []

class ActionGetVaccinationCenters(Action):
    def name(self) -> Text:
        return "action_get_vaccination_centers"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        district_id = 145  # Example: Ludhiana
        today = datetime.datetime.now().strftime("%d-%m-%Y")
        url = f"https://cdn-api.co-vin.in/api/v2/appointment/sessions/public/calendarByDistrict?district_id={district_id}&date={today}"
        headers = {"User-Agent": "Mozilla/5.0"}
        response = requests.get(url, headers=headers)

        if response.status_code == 200:
            data = response.json().get("centers", [])
            if not data:
                reply = "No vaccination centers found today in your district."
            else:
                reply = "Here are some vaccination centers:\n"
                for c in data[:5]:
                    reply += f"- {c['name']} ({c['address']}), {c['fee_type']}\n"
        else:
            reply = "Couldn't fetch vaccination data right now."
        dispatcher.utter_message(text=reply)
        return []

class ActionGetOutbreakAlerts(Action):
    def name(self) -> Text:
        return "action_get_outbreak_alerts"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        url = "https://ghoapi.azureedge.net/api/Indicator"
        try:
            response = requests.get(url)
            if response.status_code == 200:
                data = response.json()["value"]
                outbreak_indicators = [i["IndicatorName"] for i in data if "outbreak" in i["IndicatorName"].lower()]
                if outbreak_indicators:
                    reply = "🔔 Latest WHO Outbreak Indicators:\n"
                    for ind in outbreak_indicators[:5]:
                        reply += f"- {ind}\n"
                else:
                    reply = "No outbreak indicators found in WHO database."
            else:
                reply = "Could not fetch outbreak alerts."
        except Exception as e:
            reply = f"Error fetching WHO data: {str(e)}"
        
        dispatcher.utter_message(text=reply)
        return []
