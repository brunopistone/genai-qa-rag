from .Page import Page

## SearchQAPage
# This class is responsible for rendering the Search Q&A page.
# It is a child of Page.
#
class SearchQAPage(Page):
    def render(self, st, config, message_container, set_session, selected_endpoint, selected_type):
        super().render(st, config, message_container, set_session, selected_endpoint, selected_type)

        print("Render Search Q&A")

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

                    st.markdown('----')

    def render_chat(self, st, config, message_container):
        message_container.empty()

        if "chat_messages" in st.session_state and len(st.session_state["chat_messages"]) > 0:
            self.print_answer(st, config, st.session_state["chat_messages"][-1])
