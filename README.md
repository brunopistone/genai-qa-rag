# GenAI Q&A RAG

This respository implements a scalable RAG solution for a GenAI Q&A use case.


![](./images/example.png)

## Architecture

### User Interaction

![Architecture](./images/architecture_1.jpg)

### Document Indexing

![Architecture](./images/architecture_2.jpg)

## Repository Content

1. [app](./app): Streamlit app for testing the GenAI application
2. [backend](./backend): Lambda function used as backend for the GenAI application
3. [data_workflow](./data_workflow): Lambda functions used in the StepFunction workflow for indexing PDF and txt documents
4. [fargate](./fargate): Fargate content for deploying the frontend app using Fargate
5. [notebooks](./notebooks): Jupyter notebooks for testing the SageMaker Endpoints, and indexing workflows
6. [setuo](./setup): CFN template for deploying the AWS resources

## Prerequisites

1. Put the [lambda_layers](./data_workflow/lambda_layers) zip files in an Amazon S3 bucket:
   1. Option 1:
      1. Download the two layers from [Releases](https://github.com/brunopistone/genai-qa-rag/releases)
      2. [Optional] Rename each file as lambda_layer.zip
   2. Option 2:
      1. Build two .zip files starting from the requirements.txt
         1. [langchain](./backend/lambda_layers/langchain/requirements.txt)
         2. [pdf-parser-layer](./data_workflow/lambda_layers/pdf-parser-layer/requirements.txt)
      2. Download the **poppler** layer from [Releases](https://github.com/brunopistone/genai-qa-rag/releases)
      3. [Optional] Rename each file as lambda_layer.zip

2. Upload the [configs.yaml](./backend/configs.yaml) file for the Lambda backendEdit the file `configs.yaml`
   1. es_credentials: Amazon OpenSearch credentials for connecting to the ElastichSearch domain
   2. embeddings: Add the SageMaker Endpoint with the Embedding models you want to use in your application
   3. llms: Add the SageMaker Endpoint with the LLMs you want to use in your application

## Deployment

1. Deploy [cfn-template.yml](./setup/cfn-template.yml)
   1. Check the Lambda Layer Paths are reflecting your path
   2. Check the S3 bucket name is correct
   3. Edit the default CFN properties as needed
2. Edit [configs.yaml](./fargate/chat_ui/configs.yaml)
   1. aws: AWS Credentials for invoking the Lambda backend
   2. s3: Bucket info from the created Amazon S3 bucket from the point 1
3. Deploy [fargate](./fargate)
   1. `./fargate/deploy_stack.sh`