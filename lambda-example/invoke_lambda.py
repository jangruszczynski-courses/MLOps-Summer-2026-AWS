import json

import boto3
import requests


def invoke_with_boto3(function_name: str, region: str) -> dict:
    """
    Invoke the Lambda function using the AWS SDK (boto3).

    boto3 signs the request with your local AWS credentials and sends it
    directly through the AWS API — no public URL required.
    The 'Payload' in the response is the value returned by the handler.
    """
    lambda_client = boto3.client("lambda", region_name=region)

    response = lambda_client.invoke(
        FunctionName=function_name,
        InvocationType="RequestResponse",   # wait for the result
        Payload=json.dumps({}),             # empty event payload
    )

    return json.loads(response["Payload"].read())


def invoke_with_http(function_url: str) -> dict:
    """
    Invoke the Lambda function via its public Function URL using a plain
    HTTP POST request.  No AWS credentials are needed — this works like
    calling any regular web endpoint.
    """
    response = requests.post(function_url, json={}, timeout=30)
    response.raise_for_status()
    return response.json()


# ─────────────────────────────────────────────────────────────────────────────
# Fill in the variables below, then run:  python invoke_lambda.py
# FUNCTION_URL comes from the output of create_lambda.py
# ─────────────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    FUNCTION_NAME = "hello-world-lambda2"                              # same as in create_lambda.py
    FUNCTION_URL  = "https://XXX.lambda-url.us-east-1.on.aws/"  # from create_lambda.py output
    REGION        = "us-east-1"

    # print("=== Invoke via boto3 (SDK) ===")
    # result = invoke_with_boto3(FUNCTION_NAME, REGION)
    # print(result)
    # print(f"Status : {result['statusCode']}")
    # print(f"Body   : {result['body']}")

    # print()

    print("=== Invoke via HTTP (requests) ===")
    result = invoke_with_http(FUNCTION_URL)
    print(f"Message: {result.get('message')}")
