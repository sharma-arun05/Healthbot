# 🩺 HealthBot – Multilingual Preventive Healthcare Chatbot

HealthBot is an AI-powered multilingual chatbot designed to **educate rural and semi-urban populations** about:  
- Preventive healthcare  
- Disease symptoms  
- Vaccination schedules  
- Real-time outbreak alerts  

The bot integrates with **government health databases** and can send **SMS/WhatsApp alerts** via Twilio. It supports **English, Hindi, and Tamil**, making healthcare information more accessible.  

---

## ✨ Features
- 🤖 **AI-Powered NLP** – Built using [Rasa](https://rasa.com/) for natural conversations  
- 🌍 **Multilingual Support** – English, Hindi, and Tamil  
- 🦠 **Symptom Checker** – Provides disease symptom information  
- 💉 **Vaccination Info** – Age-based and region-specific schedules  
- 🔔 **Outbreak Alerts** – Real-time alerts via SMS/WhatsApp using Twilio  
- 📡 **Government API Integration** – Fetches official health information dynamically  
- 🗂 **Local Subscription Database** – Stores subscribers in SQLite for personalized alerts  

---

## 🛠 Tech Stack
- [Python 3.10+](https://www.python.org/)  
- [Rasa Open Source](https://rasa.com/)  
- [Rasa SDK](https://rasa.com/docs/rasa/custom-actions)  
- [Twilio API](https://www.twilio.com/) – SMS/WhatsApp alerts  
- [SQLite](https://www.sqlite.org/) – Local database for subscriptions  
- REST APIs (Gov health databases, WHO, CoWIN)  

---

## 📂 Project Structure
	healthbot/
├── actions/ # Custom actions (API calls, Twilio, DB)
│ └── actions.py
├── data/ # Training data
│ ├── nlu.yml
│ ├── stories.yml
│ └── rules.yml
├── tests/ # Test conversations
│ └── test_stories.yml
├── domain.yml # Intents, entities, slots, responses
├── config.yml # Rasa pipeline + policies
├── endpoints.yml # Action server settings
├── credentials.yml # Connector config (Twilio, REST) [ignored by git]
├── .env # Secrets (Twilio, Gov API keys, DB path) [ignored by git]
├── .gitignore # Ignore sensitive + generated files
└── README.md







---

## ⚙️ Setup & Installation



### 1️⃣ Clone the Repository
```bash
git clone https://github.com/your-username/HealthBot.git
cd HealthBot


   2️⃣ Create Virtual Environment
python -m venv venv
.\venv\Scripts\activate    # On Windows
# or
source venv/bin/activate   # On Linux/Mac


    3️⃣ Install Dependencies
  pip install -r requirements.txt


4️⃣ Configure Secrets

Create a .env file:

TWILIO_ACCOUNT_SID=your_twilio_sid
TWILIO_AUTH_TOKEN=your_twilio_auth_token
TWILIO_NUMBER=+1234567890
DATABASE_PATH=subscriptions.db
GOV_API_BASE=https://example.gov.health/api



5️⃣ Configure Channels

In credentials.yml:

rest:
twilio:
  account_sid: "${TWILIO_ACCOUNT_SID}"
  auth_token: "${TWILIO_AUTH_TOKEN}"
  twilio_number: "${TWILIO_NUMBER}"




🚀 Running the Bot
		Train the Model
			rasa train

		Start the Action Server
			rasa run actions

		Start the Rasa Server
			rasa run --enable-api --cors "*" -p 5005


Now your bot is live 🎉

📱 Usage

Test locally with:

			rasa shell


Send SMS/WhatsApp messages via your Twilio number

Subscribe users to outbreak alerts with:

"Subscribe me to alerts for my area"

✅ Example Queries

"What are the symptoms of dengue?"

"Which vaccines are recommended for children?"

"How can I prevent malaria?"

"Send me outbreak alerts in Hindi"






🛡 Security

.env and credentials.yml are ignored by Git to protect secrets

All sensitive keys are loaded via environment variables

Database (subscriptions.db) is stored locally







👨‍💻 Contributors

         Arun Kumar – Developer, AI/ML Engineer

📜 License

			This project is licensed under the MIT License – free to use, modify, and distribute