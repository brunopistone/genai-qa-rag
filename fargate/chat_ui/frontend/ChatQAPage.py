from .Page import Page
from utils.service import get_presigned_url

## ChatQAPage
# Class that represents the ChatQA page. Contains all the logic for rendering the chat between an AI and a Human, by
# reporting the history of the conversation and asking the user for a question, other then the sources used for generating
# the answer.
#
class ChatQAPage(Page):
    def render(self, st, config, message_container, set_session, selected_endpoint, selected_type):
        super().render(st, config, message_container, set_session, selected_endpoint, selected_type)

        print("Render Chat Q&A")

        clear_history = st.button("Clear history")

        if clear_history:
            set_session(True)

        with message_container:
            self.render_chat(st, config, message_container)

    def print_answer(self, st, config, chat_message):
        if chat_message["user"]:
            st.write(f"""
                <div style="
                    text-align: right;
                    background: #8080802e;
                    padding-top: 30px;
                    padding-bottom: 30px;
                    padding-right: 30px;
                    border-radius: 17px;">{
            chat_message["user"]}
                </div>
            """, unsafe_allow_html=True)

        if chat_message["answer"]:
            st.write(f"""
                <div id="text_message" style="margin-top: 40px; margin-bottom: 22px;">{chat_message["answer"]["answer"]}</div>
            """, unsafe_allow_html=True)

        if "sources" in chat_message["answer"] and len(chat_message["answer"]["sources"]) > 0:
            with st.expander("Sources"):
                for source in chat_message["answer"]["sources"]:
                    st.write(source["details"])
                    st.caption(source["passage"])

                    ## Checking if the answer is an image and if it is, displaying it
                    #
                    if "image" in source and source["image"] != "":
                        url = get_presigned_url(config['s3']['bucket_name'], source['image'])
                        st.image(image=url, width=300)
                    st.markdown('----')

    def print_history(self, st, config, index, chat_message):
        with st.expander(f'**Question {index}**: {chat_message["user"]}'):
            if chat_message["answer"]:
                st.write(chat_message["answer"]["answer"])

            if "sources" in chat_message["answer"] and len(chat_message["answer"]["sources"]) > 0:
                st.header("Sources:")
                for source in chat_message["answer"]["sources"]:
                    st.write(source["details"])
                    st.caption(source["passage"])

                    ## Checking if the answer is an image and if it is, displaying it
                    #
                    if "image" in source and source["image"] != "":
                        url = get_presigned_url(config['s3']['bucket_name'], source['image'])
                        st.image(image=url, width=300)
                    st.markdown('----')

    def render_chat(self, st, config, message_container):
        message_container.empty()

        index = 1

        for chat_message in st.session_state["chat_messages"]:
            if index < len(st.session_state["chat_messages"]):
                self.print_history(st, config, index, chat_message)
                index += 1
            else:
                self.print_answer(st, config, chat_message)
