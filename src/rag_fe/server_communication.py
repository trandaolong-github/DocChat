import requests
import streamlit as st

from const import (
    CHATBOT_URL_ASK,
    CHATBOT_URL_INGEST_DATA,
    CHATBOT_URL_REMOVE_DATA,
    CHATBOT_URL_AVAILABLE_MODELS,
    CHATBOT_URL_UPLOADED_FILES,
)


def get_uploaded_files():
    """List files in the uploaded_docs directory in server side."""
    try:
        resp = requests.get(CHATBOT_URL_UPLOADED_FILES)
        resp.raise_for_status()
        return resp.json()
    except requests.exceptions.HTTPError as http_err:
        st.error(f"HTTP error occurred when getting uploaded files: {http_err}")
        return []
    except Exception as e:
        st.error(f"An error occurred when getting uploaded files: {str(e)}")
        return []
    

def get_available_models():
    """Get available models from the Ollama"""
    try:
        resp = requests.get(CHATBOT_URL_AVAILABLE_MODELS)
        resp.raise_for_status()
        return resp.json()["models"]
    except requests.exceptions.HTTPError as http_err:
        st.error(f"HTTP error occurred when getting available models: {http_err}")
        return []
    except Exception as e:
        st.error(f"An error occurred when getting available models: {str(e)}")
        return []


def data_processing(api_type, data, payload=None):
    api_mapping = {
        "ingested": CHATBOT_URL_INGEST_DATA,
        "removed": CHATBOT_URL_REMOVE_DATA,
    }
    if api_type == "ingested":
        response = requests.post(api_mapping[api_type], params=payload, files=data)
    else:
        response = requests.post(api_mapping[api_type], json=data)
    response.raise_for_status()
    st.success(f"Data {api_type} successfully!")


def ask_agent(query, llm):
    """Ask the agent a question."""
    try:
        response = requests.post(
            CHATBOT_URL_ASK,
            json={
                "query": query,
                "llm": llm,
            },
        )
        response.raise_for_status()
        response_data = response.json()
        output_text = response_data["result"]
        sources = response_data["sources"]
    except requests.exceptions.HTTPError as http_err:
        if response.status_code == 404:
            output_text = """There is no data available. Please upload your files."""
        else:
            output_text = f"""An error occurred while processing your message: {http_err}
            This usually means the chatbot failed at generating a query to
            answer your question. Please try again or rephrase your message."""
        sources = []
    except Exception as e:
        output_text = f"""An unexpected error occurred: {str(e)}
        Please try again or contact support if the problem persists."""
        sources = []
    return output_text, sources


class FileUploader:
    # This is to deal with a problem with the file uploader in Streamlit:
    # every time you interact with any widget, the script is rerun
    # and you risk uploading file again. Using a session state variable:
    # allow_upload and on_change param of file_uploader to solve this.
    def __init__(self):
        self.file_uploader = st.file_uploader(
            "Choose a document to upload", 
            type=['pdf', 'txt', 'docx', 'md'],
            help="Upload a document to chat with",
            on_change=lambda: st.session_state.update({"allow_upload": True}),
        )

        self.start_upload()

    def start_upload(self):
        """Start the file upload process."""
        if self.file_uploader is not None and st.session_state.get("allow_upload"):
            content = self.file_uploader.getvalue()

            print(f"Calling ingest data api for {self.file_uploader.name}")
            try:
                data_processing(
                    "ingested",
                    {
                        "content": content,
                    },
                    {"file_name": self.file_uploader.name,}
                )
                return
            except requests.exceptions.HTTPError as http_err:
                st.error(f"HTTP error occurred: {http_err}")
            except Exception as e:
                st.error(f"An error occurred: {str(e)}")
            finally:
                st.session_state.allow_upload = False
