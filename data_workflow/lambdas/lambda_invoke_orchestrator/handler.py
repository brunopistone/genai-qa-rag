import boto3
import calendar
import json
import logging
import os
import re
import time
import traceback
from urllib.parse import unquote_plus

logger = logging.getLogger(__name__)
if len(logging.getLogger().handlers) > 0:
    logging.getLogger().setLevel(logging.INFO)
else:
    logging.basicConfig(level=logging.INFO)

step_function_client = boto3.client("stepfunctions")

document_orchestrator_arn = os.getenv("DOCUMENT_ORCHESTRATOR_ARN", default=None)

def lambda_handler(event, context):
    try:
        if "Records" in event:
            object_key = event["Records"][0]["s3"]["object"]["key"]
            object_key = unquote_plus(object_key)

            file_name = "".join(object_key.split("/")[3:])
            file_name = file_name[:68]

            execution_name = re.sub(r'[^.a-zA-Z0-9-]', "_", file_name) + "-" + str(calendar.timegm(time.gmtime()))

            response = step_function_client.start_execution(
                stateMachineArn=document_orchestrator_arn,
                name=execution_name,
                input=json.dumps(event)
            )

            logger.info(response)

            return {
                'statusCode': 200,
                'body': json.dumps("Invoked orchestrator")
            }
        else:
            return {
                'statusCode': 200,
                'body': json.dumps("Nothing to index")
            }
    except Exception as e:
        stacktrace = traceback.format_exc()
        logger.error("{}".format(stacktrace))

        return {
            'statusCode': 500,
            'body': json.dumps(stacktrace)
        }
