import time

import boto3


def create_lambda_function(
    function_name: str,
    image_uri: str,
    iam_role_arn: str,
    bucket_name: str,
    region: str,
) -> dict:
    """
    Create a Lambda function from a container image stored in ECR.

    The function receives the S3 bucket name through the BUCKET_NAME
    environment variable so the handler doesn't need it hard-coded.
    """
    lambda_client = boto3.client("lambda", region_name=region)
    response = lambda_client.create_function(
        FunctionName=function_name,
        PackageType="Image",
        Code={"ImageUri": image_uri},
        Role=iam_role_arn,
        Timeout=30,
        MemorySize=128,
        Environment={
            "Variables": {
                "BUCKET_NAME": bucket_name,
            }
        },
    )
    return response


def wait_for_active(function_name: str, region: str) -> None:
    """
    Poll until the Lambda function leaves the 'Pending' state.
    Raises RuntimeError if the function ends up in 'Failed' state.
    """
    lambda_client = boto3.client("lambda", region_name=region)
    print("Waiting for function to become active", end="", flush=True)
    while True:
        config = lambda_client.get_function_configuration(FunctionName=function_name)
        state = config["State"]
        if state == "Active":
            print(" done!")
            return
        if state == "Failed":
            raise RuntimeError(
                f"Lambda function entered Failed state: {config.get('StateReasonCode')}"
            )
        print(".", end="", flush=True)
        time.sleep(3)


def create_function_url(function_name: str, region: str) -> str:
    """
    Attach a public Function URL to the Lambda (auth type NONE) and return it.
    This URL can be called with a plain HTTP request — no AWS credentials needed.
    """
    lambda_client = boto3.client("lambda", region_name=region)

    response = lambda_client.create_function_url_config(
        FunctionName=function_name,
        AuthType="NONE",
    )

    # Grant everyone permission to call via the Function URL
    lambda_client.add_permission(
        FunctionName=function_name,
        StatementId="AllowPublicFunctionUrl",
        Action="lambda:InvokeFunctionUrl",
        Principal="*",
        FunctionUrlAuthType="NONE",
    )

    return response["FunctionUrl"]


# ─────────────────────────────────────────────────────────────────────────────
# Fill in the variables below, then run:  python create_lambda.py
# IMAGE_URI comes from the output of ecr_helper.py
# ─────────────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    FUNCTION_NAME = "hello-world-lambda2"                     # Lambda function name
    IMAGE_URI     = "XXX.dkr.ecr.us-east-1.amazonaws.com/lambda-images2:latest"  # from ecr_helper.py
    IAM_ROLE_ARN  = "arn:aws:iam::XXX:role/RoleForMyLambda"  # role the Lambda runs as
    BUCKET_NAME   = "my-bucket"                              # S3 bucket for helloworld.txt
    REGION        = "us-east-1"

    response = create_lambda_function(
        FUNCTION_NAME, IMAGE_URI, IAM_ROLE_ARN, BUCKET_NAME, REGION
    )
    print(f"Lambda function created: {response['FunctionArn']}")

    wait_for_active(FUNCTION_NAME, REGION)

    url = create_function_url(FUNCTION_NAME, REGION)
    print(f"\nFunction URL: {url}")
    print("Copy this URL into invoke_lambda.py -> FUNCTION_URL")
