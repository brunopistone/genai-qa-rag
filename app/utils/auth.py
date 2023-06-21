from streamlit_authenticator import Authenticate
import traceback

def render_auth(config):
    try:
        authenticator = Authenticate(
            config['auth']['credentials'],
            config['auth']['cookie']['name'],
            config['auth']['cookie']['key'],
            config['auth']['cookie']['expiry_days'],
        )

        return authenticator
    except Exception as e:
        stacktrace = traceback.format_exc()

        print(stacktrace)

        raise e