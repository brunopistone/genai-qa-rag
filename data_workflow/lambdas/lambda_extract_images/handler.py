import boto3
import json
import logging
import os
from pdf2image import convert_from_path
import traceback

logger = logging.getLogger(__name__)
if len(logging.getLogger().handlers) > 0:
    logging.getLogger().setLevel(logging.INFO)
else:
    logging.basicConfig(level=logging.INFO)

s3_client = boto3.client('s3')

def get_images(bucket_name, object_key):
    try:
        local_pdf_path = "/tmp/pdf_file"
        output_jpeg_path = "/tmp/images"
        if len(object_key.split("/")) == 5:
            index_name = object_key.split("/")[3]
            s3_path_pdf_images = f"{object_key.split('/')[0]}/{object_key.split('/')[1]}/images/{index_name}/{object_key.split('/')[-1]}"
        else:
            s3_path_pdf_images = f"{object_key.split('/')[0]}/{object_key.split('/')[1]}/images/{object_key.split('/')[-1]}"


        if not os.path.exists(local_pdf_path):
            os.makedirs(local_pdf_path)

        if not os.path.exists(output_jpeg_path):
            os.makedirs(output_jpeg_path)

        local_path = os.path.join(local_pdf_path, 'temp.pdf')
        s3_client.download_file(bucket_name, object_key, local_path)

        images = convert_from_path(local_path)

        results = {}
        for i, image in enumerate(images):

            # image_bytes = io.BytesIO()
            # image.save(image_bytes, format='JPEG')
            # image_bytes.seek(0)

            image.save(os.path.join(output_jpeg_path,  f"page_{i + 1}.jpeg"), format='JPEG')

            s3_key = f"{s3_path_pdf_images}/page_{i + 1}.jpeg"

            with open(os.path.join(output_jpeg_path,  f"page_{i + 1}.jpeg"), "rb") as f:
                s3_client.upload_fileobj(f, bucket_name, s3_key)

            os.remove(os.path.join(output_jpeg_path,  f"page_{i + 1}.jpeg"))

            results[str(i + 1)] = s3_key

        print(results)

        return results
    except Exception as e:
        stacktrace = traceback.format_exc()
        logger.error("{}".format(stacktrace))

        raise e

def lambda_handler(event, context):
    try:

        logger.info(event)
        status_code = event["statusCode"]

        if status_code == 200:
            event_type = event["body"]["EventType"]

            if event_type and event_type != "ObjectRemoved:Delete":
                logger.info("Extract pdf images")

                bucket_name = event["body"]["BucketName"]
                object_key = event["body"]["ObjectKey"]

                get_images(bucket_name, object_key)

                return {
                    'statusCode': 200,
                    'body': json.dumps('Indexing finished')
                }
        else:
            return event
    except Exception as e:
        stacktrace = traceback.format_exc()
        logger.error("{}".format(stacktrace))

        raise e
