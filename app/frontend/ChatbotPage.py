from .Page import Page
from utils.service import get_presigned_url
from streamlit_chat import message

## ChatbotPage
# Class that represents the Chatbot page. Contains all the logic for rendering the chat between an AI and a Human
#
class ChatbotPage(Page):
    def __init__(self):
        super().__init__()
        self.extensionsToCheck = ["fig", "figure", "figr", "image", "img", "A", "B", "C", "D", "E", "F", "G", "H", "I",
                                  "J", "K", "L", "M", "N", "O", "P", "Q", "R", "S", "T", "U", "V", "W", "X", "Y", "Z"]

    def render(self, st, config, message_container, set_session, selected_endpoint, selected_type):
        super().render(st, config, message_container, set_session, selected_endpoint, selected_type)

        print("Render Chatbot")

        self.set_system_message(st)

        clear_history = st.button("Clear history")

        if clear_history:
            set_session(True)
            self.set_system_message(st)

        with message_container:
            self.render_chat(st, config, message_container)

    def render_chat(self, st, config, message_container):
        for i in range(len(st.session_state['chat_messages'])):
            if st.session_state["chat_messages"][i]["user"] != "":
                message(st.session_state["chat_messages"][i]["user"], is_user=True, key=str(i) + '_user')
            message(st.session_state["chat_messages"][i]["answer"]["answer"], key=str(i))

    def set_system_message(self, st):
        if "system_message" not in st.session_state or not st.session_state["system_message"]:
            st.session_state["chat_messages"].append({
                "user": "",
                "answer": {
                    "answer": "Hello, I am the AWSI Chatbot, how may I help you?"
                }
            })

            st.session_state["history"].append(("Hello, who are you?", "Hello, I am the AWSI Chatbot, how may I help you?"))

            st.session_state["system_message"] = True
