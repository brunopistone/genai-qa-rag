import boto3
import json
import time
import traceback

lambda_client = boto3.client("lambda")
s3_client = boto3.client("s3")
step_function_client = boto3.client("stepfunctions")

def check_indexing_status(st, config):
    try:
        last_upload = None

        response = step_function_client.list_state_machines()

        state_machine = list(filter(lambda d: d["name"] in [config["step_functions"]["name"]], response["stateMachines"]))

        if len(state_machine) == 1:
            state_machine_arn = state_machine[0]["stateMachineArn"]

            response = step_function_client.list_executions(
                stateMachineArn=state_machine_arn
            )

            executions = response["executions"]

            if len(executions) > 0:
                if st.session_state is not None and "authentication_status" in st.session_state and \
                        st.session_state["authentication_status"] is not None and \
                        "username" in st.session_state and st.session_state["username"] is not None:
                    username = st.session_state["username"]

                    last_upload = list(filter(lambda d: d["name"].startswith(username), executions))

                    if len(last_upload) > 0:
                        last_upload = last_upload[0]
                else:
                    last_upload = executions[0]

        if last_upload:
            if last_upload["status"] == "RUNNING":
                message = st.warning("""
                    **File name**: {}  

                    **Status**: {}
                """.format(last_upload["name"], last_upload["status"]))
            elif last_upload["status"] == "SUCCEEDED":
                message = st.success("""
                    **File name**: {}  

                    **Status**: {}
                """.format(last_upload["name"], last_upload["status"]))
            else:
                message = st.error("""
                    **File name**: {}  
                      
                    **Status**: {}
                """.format(last_upload["name"], last_upload["status"]))
        else:
            message = st.error('No file uploaded yet')

        time.sleep(4)
        message.empty()

    except Exception as e:
        stacktrace = traceback.format_exc()
        print(stacktrace)

        raise e

def get_answer(st, config, selected_type, selected_endpoint, prompt):
    print("Get Answer for ", prompt)

    sources = []

    payload = {
        "user": st.session_state["username"] if "username" in st.session_state else "",
        "question": prompt,
        "chat_memory": st.session_state["history"],
        "llm_endpoint": selected_endpoint,
        "embeddings_endpoint": "GPT-J",
        "selected_type": selected_type
    }

    payload_dump = json.dumps(payload)

    response = lambda_client.invoke(
        FunctionName=config["backend"]["function_name"],
        Payload=payload_dump
    )

    print(response)

    answer = json.loads(response["Payload"].read())

    if "statusCode" in answer and answer["statusCode"] == 200:
        if "body" in answer:
            return json.loads(answer["body"])
    else:
        return {
            "answer": "Unfortunately, I can't help you with that.",
            "sources": sources
        }

def get_presigned_url(bucket_name, object_key):
    try:
        url = s3_client.generate_presigned_url(
            'get_object',
            Params={'Bucket': bucket_name,
                    'Key': object_key},
            ExpiresIn=600
        )
        return url
    except Exception as e:
        stacktrace = traceback.format_exc()
        print(stacktrace)

        raise e

def upload_file_s3(st, config, file):
    with st.spinner("Uploading to S3..."):
        bytes_data = file.read()
        file_name = file.name.replace("/", "+")
        if st.session_state is not None and "authentication_status" in st.session_state and \
                st.session_state["authentication_status"] is not None and \
                "username" in st.session_state and st.session_state["username"] is not None:
            file_path = f'{config["s3"]["path"]}/{st.session_state["username"]}/{file_name}'
        else:
            file_path = f'{config["s3"]["path"]}/{file_name}'

        print("File Name: ", file_name)
        print("S3 path: ", file_path)

        response = s3_client.put_object(
            Body=bytes_data,
            Bucket=config["s3"]["bucket_name"],
            Key=file_path)

    if response["ResponseMetadata"]["HTTPStatusCode"]:
        message = st.success('File uploaded! The content will be available in a few minutes.')
    else:
        message = st.error('Something went wrong. Please try again.')

    time.sleep(5)
    message.empty()
