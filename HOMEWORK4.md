# Homework 1 - Serverless Deployment of a Machine Learning Model

## Introduction
The goal of this assignment is to deploy a machine learning model using serverless architecture. You are free to choose any cloud provider, though guidance will focus on AWS due to its extensive serverless ecosystem and its position as the leading cloud provider by market share.

## Requirements

Your solution must implement the following workflow:
1. A serverless function (e.g., AWS Lambda) that is triggered when an image is uploaded to a cloud storage service (e.g., AWS S3 bucket)
2. The function should:
   - Download the image from the storage service
   - Perform inference using a machine learning model
   - Save the inference results back to the storage service
3. The model weights should be packaged with the function deployment (e.g., included in the Docker image) to avoid downloading them on each invocation

## Implementation Guidelines

### Setup
1. Install the necessary CLI tools for your chosen cloud provider
2. Create an account with your chosen cloud provider
3. Set up appropriate authentication and authorization for your CLI tools

### Development
1. Write the serverless function handler that will:
   - Extract information about the uploaded file from the trigger event
   - Download the file from cloud storage
   - Perform inference using your model
   - Save the results back to cloud storage
2. Create a Dockerfile to containerize your code:
   - Include the model weights in the image
   - Configure the appropriate entrypoint for your function

### Deployment
1. Build your Docker image locally
2. Test your Docker image to ensure it works as expected
3. Create a container registry repository in your cloud provider
4. Authenticate with the container registry
5. Push your Docker image to the container registry
6. Create your serverless function with the appropriate:
   - Container image reference
   - Memory allocation
   - Timeout settings
   - IAM role/permissions to access the storage service
7. Configure the storage trigger to invoke your function when files are uploaded

### Testing
1. Upload test images to your cloud storage service
2. Verify that your function is triggered
3. Check that inference results are correctly saved back to storage
4. Monitor execution logs for any errors or performance issues

## Useful Resources
- Your cloud provider's documentation for serverless functions and triggers
- Documentation for containerizing applications for serverless deployment
- Tutorials on deploying machine learning models in serverless environments
- AI assistants like Claude for help with specific implementation questions

## Submission Guidelines
- Be prepared to share your screen and demonstrate your working solution
- No formal presentation is required, but be ready to discuss:
  - Challenges encountered during implementation
  - Time-consuming aspects of the project
  - General experience and useful techniques discovered

### Useful links
- [AWS Lambda Trigger with S3](https://docs.aws.amazon.com/lambda/latest/dg/with-s3-example.html)
- [AWS CDK Examples](https://github.com/aws-samples/aws-cdk-examples/tree/main/python/lambda-s3-trigger)
- [Claude AI](https://claude.ai)
- Reference code provided in the repository
