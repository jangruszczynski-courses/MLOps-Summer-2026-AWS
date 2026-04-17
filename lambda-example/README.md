# Lambda Example

A step-by-step demo that shows students how to package a Python function as a
Docker container, publish it to AWS ECR, and deploy it as a Lambda function
that writes a file to S3.

---

## What the Lambda does

`lambda_function.py` reads the `BUCKET_NAME` environment variable and writes
`helloworld.txt` to that S3 bucket every time it is invoked.

---

## Prerequisites

| Requirement | Notes |
|---|---|
| Python 3.12+ | For running the helper scripts locally |
| [Docker](https://docs.docker.com/get-docker/) | Must be running; used to build the container image |
| AWS CLI configured | `aws configure` — the scripts use your default credentials |
| An S3 bucket | Must already exist; the Lambda writes into it |
| An IAM role for Lambda | Must have `AWSLambdaBasicExecutionRole` + `s3:PutObject` on your bucket |

Install local Python dependencies (boto3, requests):

```bash
pip install boto3 requests
# or, if you use uv:
uv sync
```

---

## Repository layout

```
lambda-example/
├── lambda_function.py   # Lambda handler — writes helloworld.txt to S3
├── Dockerfile           # Container image definition
├── requirements.txt     # Python packages installed inside the container
├── ecr_helper.py        # Step 1 — build the image and push it to ECR
├── create_lambda.py     # Step 2 — create the Lambda function in AWS
└── invoke_lambda.py     # Step 3 — invoke the Lambda two different ways
```

---

## Step 1 — Build the Docker image and push it to ECR

Open `ecr_helper.py` and fill in the three variables at the bottom of the file:

```python
if __name__ == "__main__":
    REPOSITORY_NAME = "my-lambda-repo"   # ECR repository name (created if it doesn't exist)
    REGION          = "us-east-1"        # AWS region
    LOCAL_IMAGE_TAG = "lambda-example"   # local Docker tag
```

Then run:

```bash
python ecr_helper.py
```

The script will:
1. Create the ECR repository (or reuse it if it already exists).
2. Build the Docker image targeting the `linux/amd64` platform Lambda requires.
3. Log in to ECR using short-lived credentials from boto3.
4. Tag and push the image.

At the end it prints a line like:

```
Image URI (use this in create_lambda.py):
  123456789012.dkr.ecr.us-east-1.amazonaws.com/my-lambda-repo:latest
```

Copy that URI — you need it in the next step.

---

## Step 2 — Create the Lambda function

Open `create_lambda.py` and fill in the variables at the bottom:

```python
if __name__ == "__main__":
    FUNCTION_NAME = "hello-world-lambda"
    IMAGE_URI     = "123456789012.dkr.ecr.us-east-1.amazonaws.com/my-lambda-repo:latest"  # from Step 1
    IAM_ROLE_ARN  = "arn:aws:iam::123456789012:role/my-lambda-role"  # role the Lambda assumes
    BUCKET_NAME   = "my-bucket"          # S3 bucket where helloworld.txt will be saved
    REGION        = "us-east-1"
```

Then run:

```bash
python create_lambda.py
```

The script will:
1. Create the Lambda function using the container image from ECR.
2. Pass `BUCKET_NAME` to the function as an environment variable.
3. Wait until the function reaches the `Active` state.
4. Attach a public **Function URL** (no AWS credentials needed to call it).

At the end it prints:

```
Function URL: https://xxxxxxxxxxxxxxxx.lambda-url.us-east-1.on.aws/
Copy this URL into invoke_lambda.py -> FUNCTION_URL
```

Copy that URL — you need it in the next step.

---

## Step 3 — Invoke the Lambda

Open `invoke_lambda.py` and fill in the variables at the bottom:

```python
if __name__ == "__main__":
    FUNCTION_NAME = "hello-world-lambda"                              # same as Step 2
    FUNCTION_URL  = "https://xxxxxxxx.lambda-url.us-east-1.on.aws/"  # from Step 2
    REGION        = "us-east-1"
```

Then run:

```bash
python invoke_lambda.py
```

The script demonstrates **two different ways** to call a Lambda:

### Via boto3 (AWS SDK)
`invoke_with_boto3()` uses the Lambda `Invoke` API. boto3 automatically signs
the request with your local AWS credentials. This is the typical approach
when calling Lambda from another AWS service or from a backend script.

### Via HTTP (requests)
`invoke_with_http()` sends a plain `POST` request to the Function URL. No AWS
credentials are needed — the URL behaves like any regular web endpoint. This
is useful for webhooks, browser-based clients, or any HTTP-capable caller.

Both calls should print a response similar to:

```
=== Invoke via boto3 (SDK) ===
Status : 200
Body   : {"message": "Successfully saved helloworld.txt to s3://my-bucket/helloworld.txt"}

=== Invoke via HTTP (requests) ===
Message: Successfully saved helloworld.txt to s3://my-bucket/helloworld.txt
```

---

## Verify the result

After invoking the Lambda, check your S3 bucket:

```bash
aws s3 cp s3://my-bucket/helloworld.txt - 
# expected output: Hello, World!
```

---

## IAM role — minimum permissions

The role passed as `IAM_ROLE_ARN` must trust the Lambda service and have at
least the following permissions:

```json
{
  "Effect": "Allow",
  "Action": [
    "logs:CreateLogGroup",
    "logs:CreateLogStream",
    "logs:PutLogEvents",
    "s3:PutObject"
  ],
  "Resource": [
    "arn:aws:logs:*:*:*",
    "arn:aws:s3:::my-bucket/helloworld.txt"
  ]
}
```

The trust policy must allow `lambda.amazonaws.com` to assume the role:

```json
{
  "Effect": "Allow",
  "Principal": { "Service": "lambda.amazonaws.com" },
  "Action": "sts:AssumeRole"
}
```
