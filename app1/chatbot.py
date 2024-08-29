import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.ensemble import RandomForestClassifier
from sklearn.pipeline import make_pipeline
from sklearn.model_selection import train_test_split
from .models import Ticket
import joblib
import os
import logging

# Set up logging
logger = logging.getLogger(__name__)

# Path to save and load the trained model
MODEL_PATH = os.path.join('models', 'chatbot_model.pkl')

def load_data():
    # Load data from the Django model
    tickets = Ticket.objects.all().values('hw_type', 'apps_sw', 'report_type', 'report_desc', 'act_taken')
    df = pd.DataFrame.from_records(tickets)
    
    # Preprocess data
    df['hw_type'] = df['hw_type'].str.lower().fillna('')
    df['apps_sw'] = df['apps_sw'].str.lower().fillna('')
    df['report_type'] = df['report_type'].str.lower().fillna('')
    df['report_desc'] = df['report_desc'].str.lower().fillna('')
    df['act_taken'] = df['act_taken'].str.lower().fillna('')

    # Combine problem description with hardware type and software/application
    df['combined'] = df['hw_type'] + ' ' + df['apps_sw'] + ' ' + df['report_type'] + ' ' + df['report_desc']
    
    return df

def train_model():
    df = load_data()
    
    # Split data into training and testing sets
    X_train, X_test, y_train, y_test = train_test_split(df['combined'], df['act_taken'], test_size=0.2, random_state=42)

    # Create a model pipeline
    model = make_pipeline(TfidfVectorizer(), RandomForestClassifier())
    model.fit(X_train, y_train)

    # Save the trained model to disk
    os.makedirs(os.path.dirname(MODEL_PATH), exist_ok=True)
    joblib.dump(model, MODEL_PATH)
    
    return model

def load_model():
    # Load the model from disk if it exists, otherwise train a new one
    if os.path.exists(MODEL_PATH):
        model = joblib.load(MODEL_PATH)
    else:
        model = train_model()
    
    return model

# Load the model (either from disk or train a new one)
model = load_model()

# Function to recommend action based on user input
def recommend_action(hw_type, apps_sw, report_type, report_desc):
    combined_input = hw_type + ' ' + apps_sw + ' ' + report_type + ' ' + report_desc
    action = model.predict([combined_input])[0]
    logger.info(f"Recommendation for {combined_input}: {action}")
    return action

# Function to handle user messages
def respond(hw_type, apps_sw, report_type, report_desc, chat_history):
    action = recommend_action(hw_type, apps_sw, report_type, report_desc)
    bot_message = f"Recommended Action: {action}"
    chat_history.append((f"Hardware Type: {hw_type}\nSoftware/Application: {apps_sw}\nReport Type: {report_type}\nProblem Description: {report_desc}", bot_message))
    return hw_type, apps_sw, report_type, report_desc, chat_history
