import json
import os
from typing import Any, Dict

import boto3
from botocore.client import BaseClient


def handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    AWS Lambda handler that creates a 'helloworld.txt' file in a specified S3 bucket.

    Args:
        event (Dict[str, Any]): The Lambda event payload. 
            Expected to be a dictionary, though unused in this specific logic.
        context (Any): The Lambda context object providing runtime information.  (for example how much remaining time you have)

    Returns:
        Dict[str, Any]: A standard API Gateway-style response containing 
            a status code and a JSON-serialized message body.

    Raises:
        KeyError: If the 'BUCKET_NAME' environment variable is not set.
        ClientError: If the S3 put_object operation fails due to permissions or networking.
    """
    bucket_name: str = os.environ["BUCKET_NAME"]

    # Initialize the S3 client
    s3: BaseClient = boto3.client("s3")
    
    s3.put_object(
        Bucket=bucket_name,
        Key="helloworld.txt",
        Body=b"Hello, World!",
        ContentType="text/plain",
    )

    message: str = f"Successfully saved helloworld.txt to s3://{bucket_name}/helloworld.txt"
    print(message)

    return {
        "statusCode": 200,
        "body": json.dumps({"message": message}),
    }