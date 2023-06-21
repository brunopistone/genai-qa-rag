import boto3
import logging
import time
from textractcaller.t_call import call_textract, Textract_Features
import traceback
from urllib.parse import unquote_plus

logger = logging.getLogger(__name__)
if len(logging.getLogger().handlers) > 0:
    logging.getLogger().setLevel(logging.INFO)
else:
    logging.basicConfig(level=logging.INFO)

textract_client = boto3.client("textract")

def start_textract_async(bucket_name, object_key):
    try:
        logger.info("Start textract job")

        if len(object_key.split("/")) == 5:
            output_path = "/".join(object_key.split("/")[:len(object_key.split("/")) - 3]) + "/output"
        else:
            output_path = "/".join(object_key.split("/")[:len(object_key.split("/")) - 2]) + "/output"

        logger.info("Textract output: {}".format(output_path))

        response = call_textract(
            input_document="s3://{}/{}".format(bucket_name, object_key),
            features = [Textract_Features.TABLES],
            force_async_api=True,
            return_job_id=True)

        return response
    except Exception as e:
        stacktrace = traceback.format_exc()
        logger.error("{}".format(stacktrace))

        raise e

def wait_textract_job(response):
    try:
        logger.info("Waiting textract job")

        in_progress = True
        response_text = None

        while in_progress:
            response_text = textract_client.get_document_analysis(
                JobId=response["JobId"]
            )

            if response_text["JobStatus"] == "IN_PROGRESS":
                logger.info("Job {} IN PROGRESS".format(response["JobId"]))
                time.sleep(30)
            else:
                logger.info("Job {} ended with status {}".format(response["JobId"], response_text["JobStatus"]))
                break

        logger.info("Job {} ended".format(response["JobId"]))

        return response_text
    except Exception as e:
        stacktrace = traceback.format_exc()
        logger.error("{}".format(stacktrace))

        raise e

def lambda_handler(event, context):
    try:
        logger.info(event)

        results = {
            "BucketName": None,
            "EventType": None,
            "JobId": None,
            "JobStatus": None,
            "ObjectKey": None
        }

        if "Records" in event:
            event_type = event["Records"][0]["eventName"]

            if event_type != "ObjectRemoved:Delete":
                bucket_name = event["Records"][0]["s3"]["bucket"]["name"]
                object_key = event["Records"][0]["s3"]["object"]["key"]
                object_key = unquote_plus(object_key)

                logger.info("Bucket {}".format(bucket_name))
                logger.info("Object {}".format(object_key))

                response = start_textract_async(bucket_name, object_key)

                response_text = wait_textract_job(response)

                results["BucketName"] = bucket_name
                results["EventType"] = event_type
                results["JobId"] = response["JobId"]
                results["JobStatus"] = response_text["JobStatus"]
                results["ObjectKey"] = object_key

            return {
                'statusCode': 200,
                'body': results
            }
        else:
            raise Exception("No documents to process")
    except Exception as e:
        stacktrace = traceback.format_exc()
        logger.error("{}".format(stacktrace))

        raise e
