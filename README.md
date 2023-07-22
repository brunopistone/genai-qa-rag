# GenAI Q&A RAG

This respository implements a scalable RAG solution for a GenAI Q&A use case.


![](./images/example.png)

## Architecture

### User Interaction

![Architecture](./images/architecture_1.jpg)

### Document Indexing

![Architecture](./images/architecture_2.jpg)

## Repository Content

1. [app](./app): Streamlit app for testing the GenAI application in you preferred IDE
2. [backend](./backend): Lambda function used as backend for the GenAI application
3. [data_workflow](./data_workflow): Lambda functions used in the StepFunction workflow for indexing PDF and txt documents
4. [fargate](./fargate): Fargate content for deploying the frontend app using Fargate
5. [notebooks](./notebooks): Jupyter notebooks for testing the SageMaker Endpoints, and indexing workflows
6. [setuo](./setup): CFN template for deploying the AWS resources

## Prerequisites

1. Have an existing Amazon S3 Bucket

2. Put the [lambda_layers](./data_workflow/lambda_layers) zip files in an Amazon S3 bucket:
   1. Option 1:
      1. Download the two layers from [Releases](https://github.com/brunopistone/genai-qa-rag/releases)
      2. Rename each file as lambda_layer.zip
   2. Option 2:
      1. Build two .zip files starting from the requirements.txt
         1. [langchain](./backend/lambda_layers/langchain/requirements.txt)
         2. [pdf-parser-layer](./data_workflow/lambda_layers/pdf-parser-layer/requirements.txt)
      2. Rename each file as lambda_layer.zip
   3. Put each file name in your existing Amazon S3 Bucket
      1. **gen-ai-qa/layers/langchain/lambda_layer.zip**
      2. **gen-ai-qa/layers/pdf-parser-layer/lambda_layer.zip**

## Deployment

1. Deploy [cfn-template.yml](./setup/cfn-template.yml)
   1. Check the Lambda Layer Paths are reflecting your path
   2. Provide the name of you Amazon S3 Bucket defined in the **Prerequsites1**
2. Navigate the AWS Console under Cloudformation
   1. Take the name of the resources created
      1. Amazon S3 Bucket name
      2. Amazon OpenSearch Domain Endpoint and add *https://* as prefix
3. Edit [backend/config.yaml](./backend/configs.yaml)
   1. Add **Amazon OpenSearch Domain Endpoint and add *https://* as prefix** under es_credentials -> endpoint
4. Upload [backend/config.yaml](./backend/configs.yaml) in the created Amazon S3 Bucket by the CloudFormation template under **gen-ai-qa/configs/configs.yaml**

## Optional: Deploy Fargate Application

1. Edit [configs.yaml](./fargate/chat_ui/configs.yaml)
   1. aws: AWS Credentials for invoking the Lambda backend
   2. s3: Amazon S3 Bucket name created by the Cloudformation template
2. Deploy [fargate](./fargate)
   1. `./fargate/deploy_stack.sh`