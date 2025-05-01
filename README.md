# DocChat
Chat with your document. No account, no internet required while chatting. Support docx, txt, pdf and md files

# How to run

## Setup Ollama and pull your favorite AI model
1. Go to ollama.com and download Ollama
2. Pull AI model, for example with Deepseek-r1:14b: `ollama pull deepseek-r1:14b`

## Setup and start DocChat app:
1. Clone the PR
2. Change the current directory to DocChat
3. Start the backend: `make be`
4. Start the frontend: `make fe`
5. Add your document and happy chatting !!!

## Use ngrok and Streamlit cloud for free online access (optional)
1. Create a free account on streamlit.io and ngrok.com
2. Create an app on Streamlit
3. Start the backend as described above
4. Start ngrok: `ngrok http --url=<ngrok-app-domain> <local-backend-port>`, see more details at ngrok.com
5. Update these environment variables for the Streamlit app:
```
CHATBOT_URL_ASK = "https://<ngrok-app-domain>/agent"
CHATBOT_URL_INGEST_DATA = "https://<ngrok-app-domain>/ingest_data"
CHATBOT_URL_REMOVE_DATA = "https://<ngrok-app-domain>/remove_data"
CHATBOT_URL_AVAILABLE_MODELS = "https://<ngrok-app-domain>/available_models"
CHATBOT_URL_UPLOADED_FILES = "https://<ngrok-app-domain>/uploaded_files"
```
6. Enjoy chatting !!!
