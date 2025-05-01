import streamlit as st

from server_communication import (
    ask_agent,
    data_processing,
    get_available_models,
    get_uploaded_files,
    FileUploader,
)


with st.sidebar:
    st.header("About")
    st.markdown(
        """
        This is an AI chatbot that can answer questions
        from the knowledge provided by your documents
        """
    )

    st.header("AI Model Selection")
    if "model" not in st.session_state:
        st.session_state.model = ""

    available_models = get_available_models()
    selected_model = st.selectbox(
        "Choose AI Model",
        options=available_models,
        help="Select the AI model to use for chat",
    )

    if selected_model != st.session_state.model:
        st.session_state.model = selected_model

    st.header("Document Upload")
    with st.spinner("Processing new data..."):
        FileUploader()

    # File Removal Section
    files_to_remove = get_uploaded_files()
    
    if files_to_remove:
        st.header("Remove Documents")
        files_to_delete = st.multiselect(
            "Select files to remove", 
            files_to_remove,
            help="Select one or more files to delete from the uploaded documents"
        )
        
        if st.button("Remove Selected Files"):
            for file in files_to_delete:
                print(f"Calling remove data api for {file}")
                data_processing(
                    "removed",
                    {
                        "file_name": file
                    },
                )
            st.rerun()

    # Display Available Files Section
    st.header("Current Uploaded Documents")
    available_files = get_uploaded_files()
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
    if not st.session_state.model:
        st.error("Please select a model to use.")
        st.stop()
    data = {"query": prompt, "llm": st.session_state.model}

    with st.spinner("Searching for an answer..."):
        output_text, sources = ask_agent(
            prompt,
            st.session_state.model,
        )

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
