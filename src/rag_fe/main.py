import os
import requests
import streamlit as st

DOC_DIR = os.getenv("DOC_DIR", "./uploaded_docs")

CHATBOT_URL_ASK = os.getenv("CHATBOT_URL_ASK", "http://localhost:8000/agent")
CHATBOT_URL_INGEST_DATA = os.getenv("CHATBOT_URL_DATA", "http://localhost:8000/ingest_data")
CHATBOT_URL_REMOVE_DATA = os.getenv("CHATBOT_URL_DATA", "http://localhost:8000/remove_data")


def list_uploaded_files():
    """List files in the uploaded_docs directory, excluding hidden system files."""
    return [
        f for f in os.listdir(DOC_DIR)
        if os.path.isfile(os.path.join(DOC_DIR, f)) and not f.startswith('.')
    ]


def data_processing(api_type, data):
    api_mapping = {
        "ingested": CHATBOT_URL_INGEST_DATA,
        "removed": CHATBOT_URL_REMOVE_DATA,
    }
    response = requests.post(api_mapping[api_type], json=data)
    response.raise_for_status()
    st.success(f"Data {api_type} successfully!")


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
            file_path = os.path.join(DOC_DIR, self.file_uploader.name)
            with open(file_path, "wb") as f:
                f.write(self.file_uploader.getbuffer())

            print(f"Calling ingest data api for {self.file_uploader.name}")
            try:
                data_processing(
                    "ingested",
                    {
                        "file_path": file_path,
                    },
                )
                return
            except requests.exceptions.HTTPError as http_err:
                st.error(f"HTTP error occurred: {http_err}")
            except Exception as e:
                st.error(f"An error occurred: {str(e)}")
            finally:
                st.session_state.allow_upload = False
            os.remove(file_path)


with st.sidebar:
    st.header("About")
    st.markdown(
        """
        This is an AI chatbot that can answer questions
        from the knowledge provided by your documents
        """
    )

    st.header("Document Upload")
    with st.spinner("Processing new data..."):
        FileUploader()

    # File Removal Section
    st.session_state.files_to_remove = list_uploaded_files()
    
    if st.session_state.files_to_remove:
        st.header("Remove Documents")
        files_to_delete = st.multiselect(
            "Select files to remove", 
            st.session_state.files_to_remove,
            help="Select one or more files to delete from the uploaded documents"
        )
        
        if st.button("Remove Selected Files"):
            for file in files_to_delete:
                file_path = os.path.join(DOC_DIR, file)
                try:
                    os.remove(file_path)
                    st.session_state.files_to_remove.remove(file)
                    st.success(f"Removed {file}")
                except Exception as e:
                    st.error(f"Error removing {file}: {e}")

                print(f"Calling remove data api for {file}")
                data_processing(
                    "removed",
                    {
                        "file_path": file_path
                    },
                )
            st.rerun()

    # Display Available Files Section
    st.header("Current Uploaded Documents")
    available_files = list_uploaded_files()
    if available_files:
        for file in available_files:
            st.text(f"📄 {file}")
    else:
        st.info("No documents uploaded yet.")

st.title("Ask about your document")
st.info(
    """Ask me anything relating to your documents!"""
)

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        if "output" in message.keys():
            st.markdown(message["output"])

        if "explanation" in message.keys():
            with st.status("How was this generated", state="complete"):
                st.info(message["explanation"])

if prompt := st.chat_input("What do you want to know?"):
    st.chat_message("user").markdown(prompt)

    st.session_state.messages.append({"role": "user", "output": prompt})

    data = {"text": prompt}

    with st.spinner("Searching for an answer..."):
        try:
            response = requests.post(CHATBOT_URL_ASK, json=data)
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

    st.chat_message("assistant").markdown(output_text)

    if sources:
        with st.expander("View Sources"):
            st.markdown("**Sources used to generate this answer:**")
            for source in sources:
                st.markdown(f"- {source}")

    st.session_state.messages.append(
        {
            "role": "assistant",
            "output": output_text,
            "sources": sources if sources else []
        }
    )
