import os


CHATBOT_URL_ASK = os.getenv("CHATBOT_URL_ASK", "http://localhost:8000/agent")
CHATBOT_URL_INGEST_DATA = os.getenv("CHATBOT_URL_INGEST_DATA", "http://localhost:8000/ingest_data")
CHATBOT_URL_REMOVE_DATA = os.getenv("CHATBOT_URL_REMOVE_DATA", "http://localhost:8000/remove_data")
CHATBOT_URL_AVAILABLE_MODELS = os.getenv("CHATBOT_URL_AVAILABLE_MODELS", "http://localhost:8000/available_models")
CHATBOT_URL_UPLOADED_FILES = os.getenv("CHATBOT_URL_UPLOADED_FILES", "http://localhost:8000/uploaded_files")

# For frontend deployed on Streamlit Cloud
# CHATBOT_URL_ASK = "https://antelope-flowing-partly.ngrok-free.app/agent"
# CHATBOT_URL_INGEST_DATA = "https://antelope-flowing-partly.ngrok-free.app/ingest_data"
# CHATBOT_URL_REMOVE_DATA = "https://antelope-flowing-partly.ngrok-free.app/remove_data"
# CHATBOT_URL_AVAILABLE_MODELS = "https://antelope-flowing-partly.ngrok-free.app/available_models"
# CHATBOT_URL_UPLOADED_FILES = "https://antelope-flowing-partly.ngrok-free.app/uploaded_files"
