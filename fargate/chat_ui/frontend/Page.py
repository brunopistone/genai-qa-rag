from utils import service

## Page
#   Parent class that represents a page in the application.
#   It contains the logic for rendering the page and
#   printing the chat history.
#
class Page:
    def render(self, st, config, message_container, set_session, selected_endpoint, selected_type):
        with st.form("chat_form", clear_on_submit=True):
            prompt = st.text_area(
                "Generative **AI** application using LLMs on Amazon SageMaker",
                placeholder="Enter your prompt here:",
                height=100,
                key="my_text_area"
            )

            run = st.form_submit_button("Run")

            if run and prompt:
                with st.spinner("Loading..."):
                    answer = service.get_answer(st, config, selected_type, selected_endpoint, prompt)

                    st.session_state["chat_messages"].append({
                        "user": prompt,
                        "answer": answer
                    })

                    st.session_state["history"].append((prompt, answer["answer"]))

    def print_answer(self, st, config, chat_message):
        pass

    def print_history(self, st, config, index, chat_message):
        pass

    def render_chat(self, st, config, message_container):
        pass
