from utils import auth, utils, service
from frontend import *
import streamlit as st

config = utils.read_configs("./configs.yaml")

message_container = st.container()

## set_session
#   force: bool -  Force to set session state
#   This function is used to set session state for the app.
def set_session(force=False):
    ## Set history state
    #
    if force or "chain" not in st.session_state:
        st.session_state["chain"] = {
            "built": False,
            "object": None
        }
    ## Set chat_messages state
    #
    if force or "chat_messages" not in st.session_state:
        st.session_state["chat_messages"] = []
    ## Set history state
    #
    if force or "history" not in st.session_state:
        st.session_state["history"] = []
    ## Set Chatbot system message
    #
    if force or "system_message" not in st.session_state:
        st.session_state["system_message"] = False

## render_frontend
#   This function is used to render the commin part for the frontend application, such as the sidebar and the page header.
def render_frontend():
    ## Render Page Header
    #
    with message_container:
        st.header("GenAI Q&A RAG")

    ## Render Sidebar
    #
    with st.sidebar:
        if st.session_state is not None and "authentication_status" in st.session_state and \
                st.session_state["authentication_status"] is not None:
            authenticator.logout('Logout', 'main')

        selected_type = st.selectbox(
            "Select demo type",
            ("Chat Q&A", "Chatbot"),
            on_change=set_session,
            args=(True, )
        )

        selected_endpoint = st.selectbox(
            "Select the LLM",
            (endpoint for endpoint in config["llms"]),
            on_change=set_session,
            args=(True,)
        )

        file = st.file_uploader("Choose a PDF or txt file", accept_multiple_files=False)
        st.button("Upload file to S3", on_click=service.upload_file_s3, args=(st, config, file))
        st.button("Check Indexing Status", on_click=service.check_indexing_status, args=(st, config))

    ## Render Demo Content
    #
    if selected_type == "Chat Q&A":
        page = ChatQAPage()
    else:
        page = ChatbotPage()

    page.render(st, config, message_container, set_session, selected_endpoint, selected_type)

if __name__ == "__main__":
    set_session()
    ## Check auth enabled
    #
    if config["auth"]["enable"]:
        authenticator = auth.render_auth(config)

        name, authentication_status, username = authenticator.login('Login', 'main')

        if st.session_state["authentication_status"]:
            ## Render frontend
            #
            render_frontend()
        elif st.session_state["authentication_status"] == False:
            st.error('Username/password is incorrect')
        elif st.session_state["authentication_status"] == None:
            st.warning('Please enter your username and password')
    else:
        ## Render frontend
        #
        render_frontend()
