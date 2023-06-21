import traceback
import yaml

def read_configs(file):
    try:
        with open(file, 'r') as file:
            config = yaml.safe_load(file)

        return config
    except Exception as e:
        stacktrace = traceback.format_exc()

        print(stacktrace)

        raise e
