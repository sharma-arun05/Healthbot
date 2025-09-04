from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
import os
import sqlite3
import logging
from typing import List, Dict, Any

# Assuming your actions.py is in a sub-folder named 'actions'
from actions.actions import SubscriptionDB, send_outbound_message, DATABASE_PATH

# Set up logging for the app
logging.basicConfig(level=logging.INFO)
LOG = logging.getLogger(__name__)

# Correctly configure the static folder path
# This will find the 'frontend' folder regardless of the current working directory
frontend_folder = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'frontend'))
app = Flask(__name__, static_folder=frontend_folder)

# Enable CORS for the dashboard to communicate with the server
CORS(app)

# Initialize the database connection
db = SubscriptionDB(DATABASE_PATH)

# --- Routes for the Frontend Dashboard ---

# Route to serve the main HTML page
@app.route('/')
def serve_index():
    return send_from_directory(app.static_folder, 'index.html')

# Route to serve other static files (like app.js and style.css)
@app.route('/<path:filename>')
def serve_static(filename):
    return send_from_directory(app.static_folder, filename)

# --- API Endpoints for the Dashboard's Functionality ---

@app.route('/api/subscribers', methods=['GET'])
def get_subscribers():
    """
    API endpoint to retrieve the list of all subscribed users.
    """
    try:
        subscribers = db.get_subscribers()
        return jsonify({"subscribers": subscribers})
    except sqlite3.Error as e:
        LOG.error(f"Database error while fetching subscribers: {e}")
        return jsonify({"error": "Failed to fetch subscribers"}), 500

@app.route('/api/alert', methods=['POST'])
def send_alert():
    """
    API endpoint to send an alert message to all subscribers.
    """
    try:
        data = request.get_json()
        message_text = data.get("message")
        if not message_text:
            return jsonify({"error": "Message is required"}), 400

        subscribers = db.get_subscribers()
        
        sent_count = 0
        failed_count = 0
        for subscriber in subscribers:
            phone_number = subscriber["phone_number"]
            if send_outbound_message(phone_number, message_text):
                sent_count += 1
            else:
                failed_count += 1
        
        LOG.info(f"Alert sent to {sent_count} subscribers. Failed for {failed_count}.")
        
        return jsonify({
            "status": "success",
            "message": "Alerts queued for delivery.",
            "sent": sent_count,
            "failed": failed_count
        })

    except Exception as e:
        LOG.error(f"An error occurred: {e}")
        return jsonify({"error": "An internal error occurred."}), 500

if __name__ == '__main__':
    app.run(port=5000)