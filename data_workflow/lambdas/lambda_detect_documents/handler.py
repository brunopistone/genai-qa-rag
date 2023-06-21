import logging
import traceback
from urllib.parse import unquote_plus

logger = logging.getLogger(__name__)
if len(logging.getLogger().handlers) > 0:
    logging.getLogger().setLevel(logging.INFO)
else:
    logging.basicConfig(level=logging.INFO)

def lambda_handler(event, context):
    try:
        if "Records" in event:
            object_key = event["Records"][0]["s3"]["object"]["key"]
            object_key = unquote_plus(object_key)

            if object_key.endswith(".pdf"):
                event["is_pdf"] = "true"
            elif object_key.endswith(".txt"):
                event["is_pdf"] = "false"
            else:
                raise Exception("Document type not available")

            return event
        else:
            raise Exception("No records to process")
    except Exception as e:
        stacktrace = traceback.format_exc()
        logger.error("{}".format(stacktrace))

        raise e
